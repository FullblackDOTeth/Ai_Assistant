import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

class ResearchMethods:
    def __init__(self):
        # Initialize NLTK components
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        
        # Initialize data storage
        self.quantitative_data = {}
        self.qualitative_data = {}
        self.longitudinal_data = {}
        self.case_studies = {}
        
    def experimental_research(self, independent_vars, dependent_vars, sample_size=100):
        """
        Conduct experimental research with controlled variables
        """
        # Generate synthetic data for experiment
        data = {}
        for var in independent_vars:
            data[var] = np.random.normal(0, 1, sample_size)
            
        # Create dependent variable with some relationship to independent variables
        y = sum(data[var] for var in independent_vars) + np.random.normal(0, 0.1, sample_size)
        data[dependent_vars[0]] = y
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Perform statistical analysis
        X = df[independent_vars]
        y = df[dependent_vars]
        
        # Split data and train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Generate results
        predictions = model.predict(X_test)
        r2 = r2_score(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        
        return {
            'model': model,
            'r2_score': r2,
            'mse': mse,
            'coefficients': dict(zip(independent_vars, model.coef_[0])),
            'data': df
        }
    
    def survey_analysis(self, responses, questions):
        """
        Analyze survey responses
        """
        df = pd.DataFrame(responses)
        
        analysis = {
            'summary_stats': df.describe(),
            'correlations': df.corr(),
            'frequency_counts': {col: df[col].value_counts() for col in df.columns}
        }
        
        # Generate visualizations
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.corr(), annot=True)
        plt.title('Correlation Heatmap of Survey Responses')
        plt.savefig('survey_correlations.png')
        plt.close()
        
        return analysis
    
    def longitudinal_study(self, subject_id, data_point, timestamp=None):
        """
        Add data point to longitudinal study
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        if subject_id not in self.longitudinal_data:
            self.longitudinal_data[subject_id] = []
            
        self.longitudinal_data[subject_id].append({
            'timestamp': timestamp,
            'data': data_point
        })
        
        # Analyze trends
        if len(self.longitudinal_data[subject_id]) > 1:
            timestamps = [d['timestamp'] for d in self.longitudinal_data[subject_id]]
            values = [d['data'] for d in self.longitudinal_data[subject_id]]
            
            return {
                'subject_id': subject_id,
                'data_points': len(values),
                'trend': np.polyfit(range(len(values)), values, 1)[0],
                'time_span': str(max(timestamps) - min(timestamps))
            }
    
    def case_study(self, case_id, observations, context):
        """
        Create and analyze a case study
        """
        case = {
            'id': case_id,
            'observations': observations,
            'context': context,
            'timestamp': datetime.now(),
            'analysis': self._analyze_text(observations)
        }
        
        self.case_studies[case_id] = case
        return case
    
    def ethnographic_research(self, field_notes, cultural_context):
        """
        Process ethnographic research data
        """
        analysis = {
            'themes': self._extract_themes(field_notes),
            'cultural_patterns': self._analyze_text(field_notes),
            'context': cultural_context,
            'word_frequencies': self._get_word_frequencies(field_notes)
        }
        
        return analysis
    
    def phenomenological_analysis(self, experiences):
        """
        Analyze lived experiences
        """
        themes = []
        patterns = []
        
        for experience in experiences:
            themes.extend(self._extract_themes(experience))
            patterns.extend(self._analyze_text(experience))
            
        return {
            'common_themes': Counter(themes).most_common(),
            'patterns': list(set(patterns)),
            'word_analysis': self._get_word_frequencies(' '.join(experiences))
        }
    
    def mixed_method_analysis(self, quant_data, qual_data):
        """
        Combine quantitative and qualitative analysis
        """
        quant_results = self.experimental_research(
            quant_data['independent_vars'],
            quant_data['dependent_vars'],
            quant_data.get('sample_size', 100)
        )
        
        qual_results = self.phenomenological_analysis(qual_data['experiences'])
        
        return {
            'quantitative_results': quant_results,
            'qualitative_results': qual_results,
            'integrated_insights': self._integrate_findings(quant_results, qual_results)
        }
    
    def historical_research(self, historical_data, time_period):
        """
        Analyze historical data
        """
        timeline = []
        patterns = []
        
        for event in historical_data:
            timeline.append({
                'date': event['date'],
                'event': event['description'],
                'analysis': self._analyze_text(event['description'])
            })
            
        return {
            'timeline': sorted(timeline, key=lambda x: x['date']),
            'period_analysis': self._analyze_time_period(timeline, time_period),
            'patterns': self._extract_themes('\n'.join([e['event'] for e in timeline]))
        }
    
    def grounded_theory_analysis(self, raw_data):
        """
        Develop grounded theory from data
        """
        # Initial coding
        codes = self._extract_themes(raw_data)
        
        # Axial coding (grouping related codes)
        categories = {}
        for code in codes:
            category = self._categorize_code(code)
            if category not in categories:
                categories[category] = []
            categories[category].append(code)
        
        # Selective coding (identifying core category)
        core_category = max(categories.items(), key=lambda x: len(x[1]))[0]
        
        return {
            'initial_codes': codes,
            'categories': categories,
            'core_category': core_category,
            'theory_components': self._generate_theory_components(categories, core_category)
        }
    
    def meta_analysis(self, studies):
        """
        Perform meta-analysis on multiple studies
        """
        effect_sizes = []
        weights = []
        
        for study in studies:
            effect_size = self._calculate_effect_size(study)
            weight = self._calculate_study_weight(study)
            
            effect_sizes.append(effect_size)
            weights.append(weight)
        
        weighted_mean = np.average(effect_sizes, weights=weights)
        heterogeneity = self._calculate_heterogeneity(effect_sizes, weights)
        
        return {
            'weighted_mean_effect': weighted_mean,
            'heterogeneity': heterogeneity,
            'number_of_studies': len(studies),
            'confidence_interval': self._calculate_confidence_interval(weighted_mean, weights)
        }
    
    def _analyze_text(self, text):
        """Helper method for text analysis"""
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words]
        return nltk.pos_tag(tokens)
    
    def _extract_themes(self, text):
        """Helper method to extract themes from text"""
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        meaningful_words = [w for w in tokens if w not in stop_words]
        return list(set([w for w, pos in nltk.pos_tag(meaningful_words) if pos.startswith('NN')]))
    
    def _get_word_frequencies(self, text):
        """Helper method to get word frequencies"""
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        meaningful_words = [w for w in tokens if w not in stop_words]
        return Counter(meaningful_words)
    
    def _integrate_findings(self, quant_results, qual_results):
        """Helper method to integrate quantitative and qualitative findings"""
        insights = []
        
        # Compare statistical findings with qualitative themes
        for coef, value in quant_results['coefficients'].items():
            related_themes = [theme for theme, _ in qual_results['common_themes'] 
                            if coef.lower() in theme.lower()]
            
            insights.append({
                'variable': coef,
                'statistical_impact': value,
                'related_themes': related_themes
            })
            
        return insights
    
    def _analyze_time_period(self, timeline, period):
        """Helper method to analyze historical time periods"""
        events_in_period = [event for event in timeline 
                          if period[0] <= event['date'] <= period[1]]
        
        return {
            'number_of_events': len(events_in_period),
            'themes': self._extract_themes('\n'.join([e['event'] for e in events_in_period])),
            'time_span': str(period[1] - period[0])
        }
    
    def _categorize_code(self, code):
        """Helper method to categorize codes in grounded theory"""
        # Simple categorization based on word patterns
        if any(word in code for word in ['feel', 'think', 'believe']):
            return 'cognitive'
        elif any(word in code for word in ['do', 'act', 'perform']):
            return 'behavioral'
        else:
            return 'descriptive'
    
    def _generate_theory_components(self, categories, core_category):
        """Helper method to generate theory components"""
        return {
            'core_concept': core_category,
            'related_concepts': list(categories.keys()),
            'relationships': {cat: len(items) for cat, items in categories.items()},
            'theoretical_framework': f"Theory centered on {core_category} with supporting concepts: " +
                                   ", ".join(categories.keys())
        }
    
    def _calculate_effect_size(self, study):
        """Helper method to calculate effect size"""
        if 'effect_size' in study:
            return study['effect_size']
        elif 'mean_diff' in study and 'pooled_sd' in study:
            return study['mean_diff'] / study['pooled_sd']
        else:
            return 0.0
    
    def _calculate_study_weight(self, study):
        """Helper method to calculate study weight"""
        return study.get('sample_size', 1) / study.get('variance', 1)
    
    def _calculate_heterogeneity(self, effect_sizes, weights):
        """Helper method to calculate heterogeneity"""
        weighted_mean = np.average(effect_sizes, weights=weights)
        q_stat = sum(w * (e - weighted_mean)**2 for w, e in zip(weights, effect_sizes))
        return {
            'Q_statistic': q_stat,
            'I_squared': max(0, (q_stat - len(weights) + 1) / q_stat * 100)
        }
    
    def _calculate_confidence_interval(self, mean, weights, confidence=0.95):
        """Helper method to calculate confidence interval"""
        standard_error = np.sqrt(1 / sum(weights))
        z_score = 1.96  # 95% confidence interval
        return {
            'lower': mean - z_score * standard_error,
            'upper': mean + z_score * standard_error
        }
