import os
import joblib
import pickle
from typing import Any, Dict, Optional
import hashlib
import time
from pathlib import Path

class ModelStorage:
    """
    Handles saving and loading of trained ML models locally.
    Ensures data privacy by keeping everything on the user's machine.
    """

    def __init__(self, models_dir: str = "ml_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Model metadata
        self.metadata_file = self.models_dir / "models_metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load model metadata"""
        if self.metadata_file.exists():
            try:
                import json
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return {}

    def _save_metadata(self):
        """Save model metadata"""
        try:
            import json
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _get_model_hash(self, model_name: str, model_data: Any) -> str:
        """Generate a hash for model versioning"""
        try:
            # Create a string representation for hashing
            if hasattr(model_data, 'get_params'):
                # For scikit-learn models
                params_str = str(sorted(model_data.get_params().items()))
            else:
                params_str = str(model_data)

            content = f"{model_name}_{params_str}_{time.time()}"
            return hashlib.md5(content.encode()).hexdigest()[:8]
        except:
            return str(int(time.time()))

    def save_model(self, model: Any, model_name: str, metadata: Dict = None) -> bool:
        """
        Save a trained model to disk.

        Args:
            model: The trained model object
            model_name: Name identifier for the model
            metadata: Additional metadata (accuracy, training date, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate filename with timestamp and hash
            timestamp = int(time.time())
            model_hash = self._get_model_hash(model_name, model)
            filename = f"{model_name}_{timestamp}_{model_hash}.pkl"
            filepath = self.models_dir / filename

            # Save the model
            joblib.dump(model, filepath)

            # Update metadata
            self.metadata[model_name] = {
                'filename': filename,
                'filepath': str(filepath),
                'created_at': timestamp,
                'model_hash': model_hash,
                'metadata': metadata or {}
            }

            self._save_metadata()
            print(f"Model '{model_name}' saved successfully to {filepath}")
            return True

        except Exception as e:
            print(f"Error saving model '{model_name}': {e}")
            return False

    def load_model(self, model_name: str) -> Optional[Any]:
        """
        Load a trained model from disk.

        Args:
            model_name: Name of the model to load

        Returns:
            The loaded model, or None if not found
        """
        if model_name not in self.metadata:
            print(f"Model '{model_name}' not found in storage")
            return None

        model_info = self.metadata[model_name]
        filepath = Path(model_info['filepath'])

        if not filepath.exists():
            print(f"Model file not found: {filepath}")
            return None

        try:
            model = joblib.load(filepath)
            print(f"Model '{model_name}' loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading model '{model_name}': {e}")
            return None

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a stored model"""
        return self.metadata.get(model_name)

    def list_models(self) -> Dict[str, Dict]:
        """List all stored models with their metadata"""
        return self.metadata.copy()

    def delete_model(self, model_name: str) -> bool:
        """
        Delete a stored model and its metadata.

        Args:
            model_name: Name of the model to delete

        Returns:
            True if successful, False otherwise
        """
        if model_name not in self.metadata:
            print(f"Model '{model_name}' not found")
            return False

        model_info = self.metadata[model_name]
        filepath = Path(model_info['filepath'])

        try:
            # Delete the model file
            if filepath.exists():
                filepath.unlink()

            # Remove from metadata
            del self.metadata[model_name]
            self._save_metadata()

            print(f"Model '{model_name}' deleted successfully")
            return True

        except Exception as e:
            print(f"Error deleting model '{model_name}': {e}")
            return False

    def cleanup_old_models(self, model_name: str, keep_last: int = 3):
        """
        Keep only the most recent N versions of a model.

        Args:
            model_name: Name of the model type
            keep_last: Number of recent versions to keep
        """
        # Find all models of this type
        matching_models = {}
        for name, info in self.metadata.items():
            if name.startswith(model_name):
                matching_models[name] = info

        if len(matching_models) <= keep_last:
            return

        # Sort by creation time (newest first)
        sorted_models = sorted(
            matching_models.items(),
            key=lambda x: x[1]['created_at'],
            reverse=True
        )

        # Delete older models
        for name, info in sorted_models[keep_last:]:
            self.delete_model(name)

        print(f"Cleaned up old {model_name} models, kept {keep_last} most recent")

    def get_storage_stats(self) -> Dict:
        """Get statistics about stored models"""
        total_size = 0
        model_counts = defaultdict(int)

        for name, info in self.metadata.items():
            filepath = Path(info['filepath'])
            if filepath.exists():
                total_size += filepath.stat().st_size

            # Count by model type
            base_name = name.split('_')[0]
            model_counts[base_name] += 1

        return {
            'total_models': len(self.metadata),
            'total_size_mb': total_size / (1024 * 1024),
            'models_by_type': dict(model_counts),
            'storage_path': str(self.models_dir)
        }

    def export_model(self, model_name: str, export_path: str) -> bool:
        """
        Export a model to a specified path (for backup/sharing).

        Args:
            model_name: Name of the model to export
            export_path: Path to export the model to

        Returns:
            True if successful, False otherwise
        """
        model = self.load_model(model_name)
        if model is None:
            return False

        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            joblib.dump(model, export_path)
            print(f"Model '{model_name}' exported to {export_path}")
            return True

        except Exception as e:
            print(f"Error exporting model '{model_name}': {e}")
            return False

    def import_model(self, import_path: str, model_name: str, metadata: Dict = None) -> bool:
        """
        Import a model from a file.

        Args:
            import_path: Path to the model file to import
            model_name: Name to assign to the imported model
            metadata: Additional metadata for the model

        Returns:
            True if successful, False otherwise
        """
        import_path = Path(import_path)
        if not import_path.exists():
            print(f"Import file not found: {import_path}")
            return False

        try:
            model = joblib.load(import_path)
            return self.save_model(model, model_name, metadata)

        except Exception as e:
            print(f"Error importing model from {import_path}: {e}")
            return False
