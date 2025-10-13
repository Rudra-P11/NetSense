import re
from typing import Dict, Tuple

class WebsiteClassifier:
    def __init__(self):
        self.productivity_categories = self._initialize_categories()
        
    def _initialize_categories(self) -> Dict[str, Dict]:
        return {
            'productive': {
                'keywords': [
                    'udemy', 'coursera', 'edx', 'khanacademy', 'linkedin-learning',
                    'pluralsight', 'skillshare', 'codecademy', 'freecodecamp',
                    'stackoverflow', 'github', 'gitlab', 'bitbucket', 'docs.google',
                    'scholar.google', 'arxiv', 'jstor', 'researchgate', 'medium',
                    'towardsdatascience', 'realpython', 'python.org', 'npmjs',
                    'docker', 'kubernetes', 'aws', 'azure', 'digitalocean',
                    'leetcode', 'hackerrank', 'codewars', 'datacamp', 'kaggle',
                    'notion', 'trello', 'asana', 'slack', 'teams', 'office.com',
                    'atlassian', 'jira', 'confluence', 'youtube', 'chatgpt', 'deepseek'
                ],
                'domains': [
                    'udemy.com', 'coursera.org', 'edx.org', 'khanacademy.org',
                    'linkedin.com/learning', 'pluralsight.com', 'skillshare.com',
                    'codecademy.com', 'freecodecamp.org', 'stackoverflow.com',
                    'github.com', 'gitlab.com', 'bitbucket.org', 'docs.google.com',
                    'scholar.google.com', 'arxiv.org', 'jstor.org', 'researchgate.net',
                    'leetcode.com', 'hackerrank.com', 'codewars.com', 'datacamp.com',
                    'kaggle.com', 'notion.so', 'trello.com', 'asana.com', 'youtube.com', 'chatgpt.com', 'deepseek.com'
                ]
            },
            'unproductive': {
                'keywords': [
                    'netflix', 'hulu', 'disneyplus', 'primevideo',
                    'instagram', 'tiktok', 'facebook', 'twitter', 'snapchat',
                    'pinterest', 'reddit', '9gag', 'twitch', 'discord',
                    'spotify', 'soundcloud', 'pandora', 'onlinegames',
                    'steam', 'epicgames', 'xbox', 'playstation', 'crunchyroll',
                    'funimation', 'hbomax', 'peacock', 'paramountplus',
                    'whatsapp', 'telegram', 'wechat', 'line', 'viber',
                    'porn', 'xxx', 'adult', 'dating', 'tinder', 'bumble'
                ],
                'domains': [
                    'youtu.be', 'netflix.com', 'hulu.com', 
                    'disneyplus.com', 'primevideo.com', 'instagram.com', 
                    'tiktok.com', 'facebook.com', 'twitter.com', 'snapchat.com',
                    'pinterest.com', 'reddit.com', '9gag.com', 'twitch.tv', 
                    'discord.com', 'spotify.com', 'soundcloud.com', 'pandora.com',
                    'steampowered.com', 'epicgames.com', 'xbox.com', 'playstation.com'
                ]
            },
            'neutral': {
                'keywords': [
                    'google', 'bing', 'yahoo', 'duckduckgo', 'wikipedia',
                    'news', 'weather', 'maps', 'gmail', 'outlook',
                    'hotmail', 'calendar', 'drive', 'dropbox', 'onedrive',
                    'shopping', 'amazon', 'ebay', 'walmart', 'target',
                    'banking', 'paypal', 'venmo', 'zelle', 'microsoft',
                    'apple', 'icloud', 'adobe', 'creativecloud', 'canva',
                    'booking', 'tripadvisor', 'expedia', 'airbnb', 'uber',
                    'lyft', 'doordash', 'ubereats', 'grubhub'
                ],
                'domains': [
                    'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
                    'wikipedia.org', 'gmail.com', 'outlook.com', 'hotmail.com',
                    'calendar.google.com', 'drive.google.com', 'dropbox.com',
                    'onedrive.live.com', 'amazon.com', 'ebay.com', 'walmart.com',
                    'target.com', 'paypal.com', 'venmo.com', 'microsoft.com',
                    'apple.com', 'icloud.com', 'adobe.com'
                ]
            }
        }
    
    def classify_website(self, domain: str) -> Tuple[str, float]:
        """
        Classify a website and return (category, confidence)
        """
        domain = domain.lower()
        
        scores = {'productive': 0, 'unproductive': 0, 'neutral': 0}
        
        for category, data in self.productivity_categories.items():
            # Check domains
            for cat_domain in data['domains']:
                if cat_domain in domain:
                    scores[category] += 2
            
            # Check keywords
            for keyword in data['keywords']:
                if keyword in domain:
                    scores[category] += 1
        
        # If no matches found, default to neutral
        if sum(scores.values()) == 0:
            return 'neutral', 0.5
        
        # Find the category with highest score
        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]
        total_score = sum(scores.values())
        
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        return max_category, confidence
    
    def get_productivity_analysis(self, website_data: Dict[str, float]) -> Dict:
        """
        Analyze overall productivity based on time spent on different categories
        """
        total_time = sum(website_data.values())
        category_time = {'productive': 0, 'unproductive': 0, 'neutral': 0}
        
        for domain, time_spent in website_data.items():
            category, confidence = self.classify_website(domain)
            category_time[category] += time_spent
        
        percentages = {
            category: (time / total_time * 100) if total_time > 0 else 0
            for category, time in category_time.items()
        }
        
        return {
            'category_time': category_time,
            'percentages': percentages,
            'total_time': total_time,
            'productivity_score': self._calculate_productivity_score(percentages)
        }
    
    def _calculate_productivity_score(self, percentages: Dict[str, float]) -> float:
        """
        Calculate overall productivity score (0-100)
        """
        productive_score = percentages['productive']
        unproductive_score = percentages['unproductive'] * 0.5  # Some unproductive might be breaks
        neutral_score = percentages['neutral'] * 0.7  # Neutral sites are somewhat productive
        
        return min(100, productive_score + neutral_score - unproductive_score)