import time
import re
from scapy.all import *
from scapy.layers.dns import DNSQR, DNS, DNSRR
from scapy.layers.inet import IP, TCP, UDP
from collections import defaultdict, deque
import threading
from typing import Dict, Set
import socket
from anomaly_detector import AnomalyDetector
from content_analyzer import ContentAnalyzer



class DNSSniffer:
    def __init__(self, classifier, productivity_predictor=None):
        self.classifier = classifier
        self.productivity_predictor = productivity_predictor
        self.anomaly_detector = AnomalyDetector()
        self.content_analyzer = ContentAnalyzer(enable_deep_analysis=False)  # Start with deep analysis disabled
        self.domain_activity = defaultdict(lambda: {'first_seen': 0, 'last_seen': 0, 'packet_count': 0})
        self.active_domains = set()
        self.domain_times = defaultdict(float)
        self.lock = threading.Lock()
        self.is_sniffing = False
        self.sniffer_thread = None
        self.recent_packets = deque(maxlen=1000)
        self.anomaly_alerts = deque(maxlen=100)
        self.dns_responses = {}  # Track DNS responses to map IPs to domains
        self.ssl_hostnames = {}  # Track SSL hostnames


        
    def start_sniffing(self):
        """Start packet sniffing in a separate thread"""
        self.is_sniffing = True
        self.sniffer_thread = threading.Thread(target=self._sniff_packets)
        self.sniffer_thread.daemon = True
        self.sniffer_thread.start()
        print("Packet sniffer started...")
    
    def stop_sniffing(self):
        """Stop packet sniffing"""
        self.is_sniffing = False
        if self.sniffer_thread:
            self.sniffer_thread.join(timeout=2)
        print("Packet sniffer stopped.")
    
    def _sniff_packets(self):
        """Main packet sniffing function - captures multiple types of traffic"""
        try:
            # Capture all traffic on common web ports
            filter_string = "port 53 or port 80 or port 443 or port 8080 or port 8443"
            sniff(filter=filter_string, prn=self._process_packet, store=False, 
                  stop_filter=lambda x: not self.is_sniffing)
        except Exception as e:
            print(f"Error in packet sniffing: {e}")
    
    def _extract_ssl_sni(self, data):
        """Extract Server Name Indication from TLS handshake"""
        try:
            # TLS Client Hello starts with 0x16 (handshake) 0x03 (version)
            if len(data) < 40 or data[0] != 0x16:
                return None
            
            # Skip TLS record header (5 bytes)
            pos = 5
            
            # Client Hello handshake type (1 byte)
            if pos >= len(data) or data[pos] != 0x01:
                return None
            pos += 1
            
            # Skip length (3 bytes) and version (2 bytes)
            pos += 5
            
            # Skip random (32 bytes)
            pos += 32
            
            # Session ID length
            if pos >= len(data):
                return None
            session_id_length = data[pos]
            pos += 1 + session_id_length
            
            # Cipher suites length
            if pos + 2 > len(data):
                return None
            cipher_suites_length = int.from_bytes(data[pos:pos+2], 'big')
            pos += 2 + cipher_suites_length
            
            # Compression methods length
            if pos >= len(data):
                return None
            compression_length = data[pos]
            pos += 1 + compression_length
            
            # Extensions length
            if pos + 2 > len(data):
                return None
            extensions_length = int.from_bytes(data[pos:pos+2], 'big')
            pos += 2
            
            # Parse extensions
            end_extensions = pos + extensions_length
            while pos + 4 <= end_extensions:
                ext_type = int.from_bytes(data[pos:pos+2], 'big')
                ext_length = int.from_bytes(data[pos+2:pos+4], 'big')
                
                if ext_type == 0x00:  # Server Name Indication
                    if pos + 4 + ext_length <= len(data):
                        sni_data = data[pos+4:pos+4+ext_length]
                        if len(sni_data) > 3:
                            # First 2 bytes: list length, next byte: type (0x00 for hostname)
                            if sni_data[2] == 0x00:
                                hostname_length = int.from_bytes(sni_data[3:5], 'big')
                                if 5 + hostname_length <= len(sni_data):
                                    hostname = sni_data[5:5+hostname_length].decode('utf-8', errors='ignore')
                                    return hostname
                pos += 4 + ext_length
                
        except Exception as e:
            pass
        return None
    
    def _extract_http_host(self, data):
        """Extract Host header from HTTP traffic"""
        try:
            # Try to decode as text
            text = data.decode('utf-8', errors='ignore')
            
            # Look for Host header
            host_match = re.search(r'Host:\s*([^\r\n]+)', text, re.IGNORECASE)
            if host_match:
                hostname = host_match.group(1).strip()
                return hostname
            
            # Look for absolute URL in request line
            url_match = re.search(r'^(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+https?://([^/\s]+)', text, re.IGNORECASE)
            if url_match:
                hostname = url_match.group(2).strip()
                return hostname
                
        except:
            pass
        return None
    
    def _process_dns_packet(self, packet):
        """Process DNS packets to build IP-to-domain mapping"""
        try:
            if packet.haslayer(DNS) and packet.haslayer(IP):
                dns = packet[DNS]
                
                # DNS response (contains answers)
                if dns.qr == 1 and dns.an is not None:
                    for i in range(dns.ancount):
                        if dns.an[i].type == 1:  # A record
                            domain = dns.an[i].rrname.decode('utf-8').rstrip('.')
                            ip = dns.an[i].rdata
                            
                            if self._is_actual_domain(domain):
                                self.dns_responses[ip] = domain
                                return domain
                                
        except Exception as e:
            pass
        return None
    
    def _is_actual_domain(self, domain):
        """Check if this is an actual website domain, not CDN/reverse DNS"""
        if not domain or len(domain) < 4:
            return False
            
        domain_lower = domain.lower()
        
        # Skip reverse DNS, CDNs, and internal domains
        skip_patterns = [
            'in-addr.arpa', 'compute.amazonaws.com', 'amazonaws.com',
            'akamaitechnologies.com', 'akamaiedge.net', 'edgekey.net',
            'cloudfront.net', '1e100.net', 'googleusercontent.com',
            'gstatic.com', 'googleapis.com', 'cloudflare.com',
            'fastly.net', 'cdn.cloudflare.net', 'msn.com',
            'windows.com', 'microsoft.com', 'live.com',
            'msftconnecttest.com', 'connectivitycheck.com'
        ]
        
        for pattern in skip_patterns:
            if pattern in domain_lower:
                return False
        
        # Should be a proper domain with at least one dot
        if '.' not in domain_lower:
            return False
            
        # Should not be an IP address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain_lower):
            return False
            
        # Should not have too many subdomains (likely CDN)
        if domain_lower.count('.') > 3:
            return False
            
        return True
    
    def _clean_domain(self, domain):
        """Clean and normalize domain"""
        if not domain:
            return None
            
        domain = domain.lower().strip()
        
        # Remove www prefix for consistency
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    
    def _process_packet(self, packet):
        """Process individual packets and extract actual domains"""
        try:
            domain = None
            current_time = time.time()
            
            # Method 1: DNS responses (most reliable)
            if packet.haslayer(DNS):
                domain = self._process_dns_packet(packet)
            
            # Method 2: SSL/TLS SNI (for HTTPS sites)
            if not domain and packet.haslayer(TCP) and packet.haslayer(Raw):
                tcp = packet[TCP]
                # Look for TLS on HTTPS port or any port with Client Hello
                if tcp.dport == 443 or tcp.sport == 443 or len(packet[Raw]) > 40:
                    ssl_domain = self._extract_ssl_sni(bytes(packet[Raw]))
                    if ssl_domain and self._is_actual_domain(ssl_domain):
                        domain = ssl_domain
            
            # Method 3: HTTP Host headers
            if not domain and packet.haslayer(TCP) and packet.haslayer(Raw):
                tcp = packet[TCP]
                if tcp.dport == 80 or tcp.sport == 80:  # HTTP
                    http_domain = self._extract_http_host(bytes(packet[Raw]))
                    if http_domain and self._is_actual_domain(http_domain):
                        domain = http_domain
            
            # Method 4: Map IP to domain using DNS responses
            if not domain and packet.haslayer(IP):
                ip = packet[IP].dst
                if ip in self.dns_responses:
                    domain = self.dns_responses[ip]
            
            # Clean and validate the domain
            if domain:
                domain = self._clean_domain(domain)
                if domain and self._is_actual_domain(domain):
                    self._record_domain_activity(domain, packet, current_time)
                        
        except Exception as e:
            # Don't print every error to avoid spam
            pass
    
    def _record_domain_activity(self, domain, packet, current_time):
        """Record domain activity in a thread-safe manner"""
        with self.lock:
            # Update domain activity
            if domain not in self.domain_activity:
                self.domain_activity[domain]['first_seen'] = current_time
            
            self.domain_activity[domain]['last_seen'] = current_time
            self.domain_activity[domain]['packet_count'] += 1
            
            # Track active domains for time calculation
            if domain not in self.active_domains:
                self.active_domains.add(domain)
                self.domain_activity[domain]['session_start'] = current_time
            else:
                # Calculate time spent since last activity
                session_start = self.domain_activity[domain].get('session_start', current_time)
                time_spent = current_time - session_start
                self.domain_times[domain] += time_spent
                self.domain_activity[domain]['session_start'] = current_time
            
            # Store packet info
            src_ip = packet[IP].src if packet.haslayer(IP) else 'Unknown'
            dst_ip = packet[IP].dst if packet.haslayer(IP) else 'Unknown'
            
            protocol = 'DNS' if packet.haslayer(DNS) else 'HTTP' if packet[TCP].dport == 80 else 'HTTPS'
            
            self.recent_packets.append({
                'timestamp': current_time,
                'domain': domain,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'protocol': protocol
            })

            # Anomaly detection
            packet_info = {
                'timestamp': current_time,
                'protocol': protocol,
                'category': self.classifier.classify_website(domain)[0]  # Get category
            }
            is_anomaly, score, message = self.anomaly_detector.detect_anomaly(domain, packet_info, self.domain_activity[domain])
            if is_anomaly:
                alert = {
                    'timestamp': current_time,
                    'domain': domain,
                    'anomaly_score': score,
                    'alert_message': message,
                    'packet_info': packet_info
                }
                self.anomaly_alerts.append(alert)
                print(f"ANOMALY DETECTED: {domain} - {message}")

            # Content analysis (if enabled and consented)
            if packet.haslayer(Raw):
                content_insights = self.content_analyzer.analyze_payload(domain, bytes(packet[Raw]), protocol)
                if content_insights:
                    # Store content insights if needed
                    pass

            # Print for debugging
            print(f"Captured: {domain} via {protocol}")


    
    def get_domain_statistics(self) -> Dict:
        """Get statistics about captured domains"""
        with self.lock:
            current_time = time.time()

            # Calculate time for currently active domains
            for domain in list(self.active_domains):
                session_start = self.domain_activity[domain].get('session_start', current_time)
                additional_time = current_time - session_start
                self.domain_times[domain] += additional_time
                self.domain_activity[domain]['session_start'] = current_time

            # Filter out domains with very little time and clean them
            domain_data = {}
            for domain, time_spent in self.domain_times.items():
                if time_spent > 3:  # Only include domains with more than 3 seconds
                    clean_domain = self._clean_domain(domain)
                    if clean_domain and self._is_actual_domain(clean_domain):
                        domain_data[clean_domain] = time_spent

            return {
                'domain_times': domain_data,
                'total_domains': len(domain_data),
                'total_packets': sum(activity['packet_count'] for activity in self.domain_activity.values()),
                'recent_activity': list(self.recent_packets)[-15:],  # Last 15 activities
                'anomaly_stats': self.get_anomaly_stats()
            }

    
    def get_productivity_analysis(self):
        """Get productivity analysis based on domain times"""
        stats = self.get_domain_statistics()
        productivity_analysis = self.classifier.get_productivity_analysis(stats['domain_times'])

        # Add productivity data to predictor if available
        if self.productivity_predictor:
            productivity_score = productivity_analysis.get('productivity_score', 0)
            if productivity_score > 0:  # Only add meaningful data
                # Create context with domain times
                context = {
                    'domain_times': stats['domain_times'],
                    'total_domains': stats['total_domains'],
                    'total_packets': stats['total_packets']
                }
                self.productivity_predictor.add_productivity_data(
                    productivity_score=productivity_score,
                    context=context
                )

        return productivity_analysis
    
    def get_anomaly_stats(self) -> Dict:
        """Get anomaly detection statistics"""
        detector_stats = self.anomaly_detector.get_anomaly_stats()
        # Override with our own alerts since we store them here
        detector_stats['total_alerts'] = len(self.anomaly_alerts)
        detector_stats['recent_alerts'] = list(self.anomaly_alerts)[-10:]  # Last 10 alerts
        # Calculate alerts_per_hour from our alerts
        if len(self.anomaly_alerts) > 1:
            time_span = self.anomaly_alerts[-1]['timestamp'] - self.anomaly_alerts[0]['timestamp']
            detector_stats['alerts_per_hour'] = (len(self.anomaly_alerts) / time_span) * 3600 if time_span > 0 else 0
        else:
            detector_stats['alerts_per_hour'] = 0
        return detector_stats


    def update_anomaly_baseline(self) -> bool:
        """Update the anomaly detection baseline"""
        return self.anomaly_detector.update_baseline()

    def enable_deep_analysis(self, enabled: bool):
        """Enable or disable deep content analysis"""
        self.content_analyzer.enable_deep_analysis = enabled

    def add_content_consent(self, domain: str):
        """Add consent for content analysis of a domain"""
        self.content_analyzer.add_consent(domain)

    def remove_content_consent(self, domain: str):
        """Remove consent for content analysis of a domain"""
        self.content_analyzer.remove_consent(domain)

    def get_content_insights(self, domain: str = None):
        """Get content analysis insights"""
        if domain:
            return self.content_analyzer.get_domain_insights(domain)
        else:
            return self.content_analyzer.get_content_statistics()

    def clear_content_data(self, domain: str = None):
        """Clear content analysis data"""
        if domain:
            self.content_analyzer.clear_domain_data(domain)
        else:
            self.content_analyzer.clear_all_data()

    def clear_statistics(self):
        """Clear all collected statistics"""
        with self.lock:
            self.domain_activity.clear()
            self.active_domains.clear()
            self.domain_times.clear()
            self.recent_packets.clear()
            self.anomaly_alerts.clear()
            self.dns_responses.clear()
            self.anomaly_detector.clear_data()
            self.content_analyzer.clear_all_data()

    def get_content_stats(self) -> Dict:
        """Get content analysis statistics"""
        return self.content_analyzer.get_content_statistics()

    def analyze_domain_content(self, domain: str, deep_analysis: bool = False) -> Dict:
        """Analyze content for a specific domain"""
        try:
            if deep_analysis:
                self.enable_deep_analysis(True)
                self.add_content_consent(domain)

            # Get existing insights for the domain
            insights = self.get_content_insights(domain)

            if insights and insights.get('sample_count', 0) > 0:
                # Format for dashboard display
                sentiment = insights.get('average_sentiment', {})
                compound_score = sentiment.get('compound', 0)

                # Determine overall sentiment
                if compound_score >= 0.05:
                    overall_sentiment = 'positive'
                elif compound_score <= -0.05:
                    overall_sentiment = 'negative'
                else:
                    overall_sentiment = 'neutral'

                # Calculate confidence based on sample count
                sample_count = insights.get('sample_count', 0)
                confidence = min(sample_count / 10.0, 1.0)  # Scale confidence with sample count

                # Get sample content (up to 3 samples, truncated to 200 chars each)
                text_samples = insights.get('text_samples', [])[:3]
                sample_content = []
                for sample in text_samples:
                    if len(sample) > 200:
                        sample_content.append(sample[:200] + "...")
                    else:
                        sample_content.append(sample)

                # Get top keywords
                top_keywords = [kw for kw, _ in insights.get('top_keywords', [])]

                # Get content categories
                top_categories = [cat for cat, _ in insights.get('top_categories', [])]

                # Enhanced summary with detailed info
                summary_parts = [
                    f"Analyzed {sample_count} content samples.",
                    f"Overall sentiment: {overall_sentiment.title()} (confidence: {confidence:.1f})."
                ]

                if top_keywords:
                    summary_parts.append(f"Top keywords: {', '.join(top_keywords[:5])}.")

                if top_categories:
                    summary_parts.append(f"Content categories: {', '.join(top_categories[:3])}.")

                # Add sentiment trend if available
                trend = insights.get('sentiment_trend', 'unknown')
                if trend != 'insufficient_data':
                    summary_parts.append(f"Sentiment trend: {trend.title()}.")

                summary = " ".join(summary_parts)

                return {
                    'domain': domain,
                    'sentiment': overall_sentiment,
                    'confidence': confidence,
                    'keywords': top_keywords,
                    'categories': top_categories,
                    'summary': summary,
                    'timestamp': insights.get('last_analyzed', time.time()),
                    'sample_content': sample_content,
                    'sample_count': sample_count,
                    'sentiment_trend': trend,
                    'total_packets_analyzed': insights.get('total_packets_analyzed', 0)
                }
            else:
                # Return default result when no data is available
                return {
                    'domain': domain,
                    'sentiment': 'unknown',
                    'confidence': 0.0,
                    'keywords': [],
                    'categories': [],
                    'summary': f"No content data available for {domain}. Enable deep analysis and visit the domain to collect data.",
                    'timestamp': time.time(),
                    'sample_content': [],
                    'sample_count': 0,
                    'sentiment_trend': 'unknown',
                    'total_packets_analyzed': 0
                }
        except Exception as e:
            # Return error result for dashboard to handle gracefully
            return {
                'domain': domain,
                'sentiment': 'error',
                'confidence': 0.0,
                'keywords': [],
                'categories': [],
                'summary': f"Error analyzing content for {domain}: {str(e)}",
                'timestamp': time.time(),
                'sample_content': [],
                'sample_count': 0,
                'sentiment_trend': 'unknown',
                'total_packets_analyzed': 0
            }
