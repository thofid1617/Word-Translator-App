from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
from typing import Dict, List

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class TranslationPredictor:
    """
    Translation predictor using Google Translate API or local translation logic
    For demo purposes, using a simple mock translation service
    """
    
    def __init__(self):
        # Language mapping for common languages
        self.languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
        
        # Simple mock translations for demo
        self.mock_translations = {
            ('hello', 'en', 'es'): 'hola',
            ('hello', 'en', 'fr'): 'bonjour',
            ('hello', 'en', 'de'): 'hallo',
            ('goodbye', 'en', 'es'): 'adiós',
            ('goodbye', 'en', 'fr'): 'au revoir',
            ('thank you', 'en', 'es'): 'gracias',
            ('thank you', 'en', 'fr'): 'merci',
            ('how are you', 'en', 'es'): 'cómo estás',
            ('good morning', 'en', 'es'): 'buenos días',
            ('good night', 'en', 'es'): 'buenas noches'
        }
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection (mock implementation)
        In production, use langdetect library or Google Cloud Translate API
        """
        # Simple heuristic based on common words
        english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it']
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'es', 'en', 'un', 'ser']
        french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en']
        
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_words if word in text_lower)
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        french_count = sum(1 for word in french_words if word in text_lower)
        
        if english_count > spanish_count and english_count > french_count:
            return 'en'
        elif spanish_count > french_count:
            return 'es'
        elif french_count > 0:
            return 'fr'
        else:
            return 'en'  # Default to English
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """
        Translate text from source language to target language
        """
        if source_lang == target_lang:
            return {
                'translated_text': text,
                'confidence': 1.0,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
        
        # Check mock translations first
        text_lower = text.lower().strip()
        mock_key = (text_lower, source_lang, target_lang)
        
        if mock_key in self.mock_translations:
            return {
                'translated_text': self.mock_translations[mock_key],
                'confidence': 0.95,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
        
        # For demo purposes, return a placeholder translation
        # In production, integrate with Google Translate API, Azure Translator, etc.
        return {
            'translated_text': f"[Translation of '{text}' from {source_lang} to {target_lang}]",
            'confidence': 0.7,
            'source_lang': source_lang,
            'target_lang': target_lang
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Return supported languages"""
        return self.languages

# Initialize translator
translator = TranslationPredictor()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'success': True,
        'languages': translator.get_supported_languages()
    })

@app.route('/api/detect', methods=['POST'])
def detect_language():
    """Detect language of input text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        detected_lang = translator.detect_language(text)
        
        return jsonify({
            'success': True,
            'detected_language': detected_lang,
            'language_name': translator.languages.get(detected_lang, 'Unknown'),
            'text': text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text between languages"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        # Auto-detect source language if needed
        if source_lang == 'auto':
            source_lang = translator.detect_language(text)
        
        # Perform translation
        result = translator.translate_text(text, source_lang, target_lang)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': result['translated_text'],
            'source_language': source_lang,
            'source_language_name': translator.languages.get(source_lang, 'Unknown'),
            'target_language': target_lang,
            'target_language_name': translator.languages.get(target_lang, 'Unknown'),
            'confidence': result['confidence']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/translate_batch', methods=['POST'])
def translate_batch():
    """Translate multiple texts at once"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')
        
        if not texts:
            return jsonify({
                'success': False,
                'error': 'No texts provided'
            }), 400
        
        results = []
        for text in texts:
            if text.strip():
                # Auto-detect if needed
                current_source = source_lang
                if source_lang == 'auto':
                    current_source = translator.detect_language(text)
                
                result = translator.translate_text(text, current_source, target_lang)
                results.append({
                    'original_text': text,
                    'translated_text': result['translated_text'],
                    'source_language': current_source,
                    'confidence': result['confidence']
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'target_language': target_lang,
            'target_language_name': translator.languages.get(target_lang, 'Unknown')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
