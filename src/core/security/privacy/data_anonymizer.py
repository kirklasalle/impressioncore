# Phase 8A Week 2: Data Anonymizer
# File: src/security/privacy/data_anonymizer.py
# Description: Data anonymization and pseudonymization tools
# Created: 2025-01-18 22:20:00 UTC
# Author: GitHub Copilot (ImpressionCore)

"""
Data Anonymizer System

Implements comprehensive data anonymization and pseudonymization techniques
for privacy protection, including k-anonymity, l-diversity, differential privacy,
and secure data transformation methods. Optimized for GTX 1050 Ti constraints.

Features:
- K-anonymity and l-diversity enforcement
- Differential privacy mechanisms
- Data suppression and generalization
- Pseudonymization with secure key management
- Reversible and irreversible anonymization
- Performance-optimized batch processing

Memory Target: <25MB for temporary operations and buffers
"""

import logging
import asyncio
import hashlib
import json
import time
import random
import math
from typing import Dict, List, Set, Optional, Union, Any, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
import threading
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import secrets
import string

logger = logging.getLogger(__name__)

class AnonymizationMethod(Enum):
    """Types of anonymization methods."""
    SUPPRESSION = "suppression"  # Remove sensitive data
    GENERALIZATION = "generalization"  # Reduce precision
    PSEUDONYMIZATION = "pseudonymization"  # Replace with pseudonyms
    NOISE_ADDITION = "noise_addition"  # Add statistical noise
    SHUFFLING = "shuffling"  # Shuffle attribute values
    SUBSTITUTION = "substitution"  # Replace with synthetic values
    DIFFERENTIAL_PRIVACY = "differential_privacy"  # Add calibrated noise

class DataType(Enum):
    """Types of data for anonymization."""
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    DATE = "date"
    TEXT = "text"
    IDENTIFIER = "identifier"
    QUASI_IDENTIFIER = "quasi_identifier"
    SENSITIVE = "sensitive"

@dataclass
class AnonymizationRule:
    """Represents an anonymization rule for a data field."""
    field_name: str
    data_type: DataType
    method: AnonymizationMethod
    parameters: Dict[str, Any]
    is_reversible: bool = False
    key_id: Optional[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class AnonymizationConfig:
    """Configuration for anonymization process."""
    k_anonymity: int = 5
    l_diversity: int = 2
    epsilon: float = 1.0  # Differential privacy parameter
    delta: float = 1e-5  # Differential privacy parameter
    suppression_threshold: float = 0.1
    generalization_levels: int = 3
    preserve_utility: bool = True
    reversible_fields: List[str] = None
    
    def __post_init__(self):
        if self.reversible_fields is None:
            self.reversible_fields = []

@dataclass
class AnonymizationResult:
    """Result of anonymization operation."""
    original_records: int
    anonymized_records: int
    suppressed_records: int
    anonymization_level: str
    utility_score: float
    privacy_score: float
    method_summary: Dict[str, int]
    execution_time_ms: int
    memory_used_mb: float

class DataAnonymizer:
    """
    Comprehensive data anonymization system with privacy preservation.
    
    Implements multiple anonymization techniques with configurable privacy
    and utility trade-offs, optimized for memory-constrained environments.
    """
    
    def __init__(self, config: Optional[AnonymizationConfig] = None):
        """Initialize data anonymizer."""
        self.config = config or AnonymizationConfig()
        self.memory_limit_mb = 25
        self.pseudonym_cache = {}  # Cache for pseudonyms
        self.generalization_hierarchies = {}
        self.keys = {}  # Encryption keys for reversible anonymization
        self.lock = threading.RLock()
        
        # Performance tracking
        self.stats = {
            'anonymizations_performed': 0,
            'records_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'memory_peak_mb': 0,
            'last_cleanup': time.time()
        }
        
        # Initialize default hierarchies
        self._init_generalization_hierarchies()
        
        logger.info("Data anonymizer initialized")
    
    def _init_generalization_hierarchies(self):
        """Initialize default generalization hierarchies."""
        # Age generalization hierarchy
        self.generalization_hierarchies['age'] = {
            'levels': [
                lambda x: x,  # Original value
                lambda x: f"{(x // 5) * 5}-{(x // 5) * 5 + 4}",  # 5-year ranges
                lambda x: f"{(x // 10) * 10}-{(x // 10) * 10 + 9}",  # 10-year ranges
                lambda x: f"{(x // 20) * 20}-{(x // 20) * 20 + 19}",  # 20-year ranges
                lambda x: "adult" if x >= 18 else "minor"  # Adult/minor
            ]
        }
        
        # Date generalization hierarchy
        self.generalization_hierarchies['date'] = {
            'levels': [
                lambda x: x.strftime('%Y-%m-%d'),  # Full date
                lambda x: x.strftime('%Y-%m'),  # Year-month
                lambda x: x.strftime('%Y'),  # Year only
                lambda x: f"{(x.year // 5) * 5}s",  # 5-year periods
                lambda x: f"{(x.year // 10) * 10}s"  # Decades
            ]
        }
        
        # Income generalization hierarchy
        self.generalization_hierarchies['income'] = {
            'levels': [
                lambda x: x,  # Original value
                lambda x: f"{(x // 10000) * 10000}-{(x // 10000) * 10000 + 9999}",  # 10k ranges
                lambda x: f"{(x // 25000) * 25000}-{(x // 25000) * 25000 + 24999}",  # 25k ranges
                lambda x: f"{(x // 50000) * 50000}-{(x // 50000) * 50000 + 49999}",  # 50k ranges
                lambda x: "high" if x > 100000 else "medium" if x > 50000 else "low"  # Categories
            ]
        }
        
        # ZIP code generalization hierarchy
        self.generalization_hierarchies['zipcode'] = {
            'levels': [
                lambda x: x,  # Full ZIP
                lambda x: x[:4] + "*",  # First 4 digits
                lambda x: x[:3] + "**",  # First 3 digits
                lambda x: x[:2] + "***",  # First 2 digits
                lambda x: x[:1] + "****"  # First digit only
            ]
        }
    
    def anonymize_dataset(self, data: pd.DataFrame, rules: List[AnonymizationRule]) -> AnonymizationResult:
        """Anonymize a complete dataset using specified rules."""
        start_time = time.time()
        initial_records = len(data)
        
        try:
            # Create working copy
            anonymized_data = data.copy()
            method_summary = defaultdict(int)
            
            # Apply anonymization rules
            for rule in rules:
                if rule.field_name in anonymized_data.columns:
                    anonymized_data, applied_method = self._apply_rule(anonymized_data, rule)
                    method_summary[applied_method] += 1
            
            # Enforce k-anonymity if required
            if self.config.k_anonymity > 1:
                anonymized_data = self._enforce_k_anonymity(anonymized_data, rules)
            
            # Enforce l-diversity if required
            if self.config.l_diversity > 1:
                anonymized_data = self._enforce_l_diversity(anonymized_data, rules)
            
            # Calculate metrics
            final_records = len(anonymized_data)
            suppressed_records = initial_records - final_records
            
            execution_time = int((time.time() - start_time) * 1000)
            memory_used = self._estimate_memory_usage(anonymized_data)
            
            # Calculate utility and privacy scores
            utility_score = self._calculate_utility_score(data, anonymized_data)
            privacy_score = self._calculate_privacy_score(anonymized_data, rules)
            
            # Update statistics
            self.stats['anonymizations_performed'] += 1
            self.stats['records_processed'] += initial_records
            self.stats['memory_peak_mb'] = max(self.stats['memory_peak_mb'], memory_used)
            
            result = AnonymizationResult(
                original_records=initial_records,
                anonymized_records=final_records,
                suppressed_records=suppressed_records,
                anonymization_level=self._determine_anonymization_level(rules),
                utility_score=utility_score,
                privacy_score=privacy_score,
                method_summary=dict(method_summary),
                execution_time_ms=execution_time,
                memory_used_mb=memory_used
            )
            
            logger.info(f"Dataset anonymized: {initial_records} -> {final_records} records")
            return result
            
        except Exception as e:
            logger.error(f"Dataset anonymization failed: {e}")
            raise
    
    def _apply_rule(self, data: pd.DataFrame, rule: AnonymizationRule) -> Tuple[pd.DataFrame, str]:
        """Apply a single anonymization rule to data."""
        field_name = rule.field_name
        method = rule.method
        
        if method == AnonymizationMethod.SUPPRESSION:
            return self._apply_suppression(data, rule), "suppression"
        
        elif method == AnonymizationMethod.GENERALIZATION:
            return self._apply_generalization(data, rule), "generalization"
        
        elif method == AnonymizationMethod.PSEUDONYMIZATION:
            return self._apply_pseudonymization(data, rule), "pseudonymization"
        
        elif method == AnonymizationMethod.NOISE_ADDITION:
            return self._apply_noise_addition(data, rule), "noise_addition"
        
        elif method == AnonymizationMethod.SHUFFLING:
            return self._apply_shuffling(data, rule), "shuffling"
        
        elif method == AnonymizationMethod.SUBSTITUTION:
            return self._apply_substitution(data, rule), "substitution"
        
        elif method == AnonymizationMethod.DIFFERENTIAL_PRIVACY:
            return self._apply_differential_privacy(data, rule), "differential_privacy"
        
        else:
            logger.warning(f"Unknown anonymization method: {method}")
            return data, "none"
    
    def _apply_suppression(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply suppression anonymization."""
        field_name = rule.field_name
        threshold = rule.parameters.get('threshold', self.config.suppression_threshold)
        
        # Remove records that appear infrequently
        value_counts = data[field_name].value_counts()
        frequent_values = value_counts[value_counts >= threshold * len(data)].index
        
        suppressed_data = data[data[field_name].isin(frequent_values)].copy()
        
        # Optionally replace with placeholder
        if rule.parameters.get('use_placeholder', False):
            placeholder = rule.parameters.get('placeholder', '*')
            suppressed_data.loc[~suppressed_data[field_name].isin(frequent_values), field_name] = placeholder
            return data.copy()  # Return original with placeholders
        
        return suppressed_data
    
    def _apply_generalization(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply generalization anonymization."""
        field_name = rule.field_name
        level = rule.parameters.get('level', 1)
        hierarchy_name = rule.parameters.get('hierarchy', field_name)
        
        if hierarchy_name in self.generalization_hierarchies:
            hierarchy = self.generalization_hierarchies[hierarchy_name]
            if level < len(hierarchy['levels']):
                generalization_func = hierarchy['levels'][level]
                data[field_name] = data[field_name].apply(generalization_func)
        else:
            # Default generalization for unknown hierarchies
            if rule.data_type == DataType.NUMERICAL:
                # Reduce precision
                precision = rule.parameters.get('precision', 1)
                data[field_name] = (data[field_name] // precision) * precision
            elif rule.data_type == DataType.TEXT:
                # Truncate text
                max_length = rule.parameters.get('max_length', 10)
                data[field_name] = data[field_name].astype(str).str[:max_length]
        
        return data
    
    def _apply_pseudonymization(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply pseudonymization anonymization."""
        field_name = rule.field_name
        is_reversible = rule.is_reversible
        key_id = rule.key_id or f"{field_name}_key"
        
        # Generate or retrieve pseudonymization key
        if key_id not in self.keys:
            self.keys[key_id] = secrets.token_bytes(32)
        
        key = self.keys[key_id]
        
        # Create pseudonyms
        unique_values = data[field_name].unique()
        pseudonym_map = {}
        
        for value in unique_values:
            if is_reversible:
                # Use HMAC for reversible pseudonymization
                pseudonym = hashlib.pbkdf2_hmac('sha256', str(value).encode(), key, 100000)
                pseudonym = pseudonym.hex()[:16]  # Take first 16 chars
            else:
                # Use SHA256 for irreversible pseudonymization
                combined = str(value) + key.hex()
                pseudonym = hashlib.sha256(combined.encode()).hexdigest()[:16]
            
            pseudonym_map[value] = f"PSEUDO_{pseudonym}"
        
        # Apply pseudonymization
        data[field_name] = data[field_name].map(pseudonym_map)
        
        # Cache for potential reversibility
        if is_reversible:
            cache_key = f"{field_name}_{key_id}"
            self.pseudonym_cache[cache_key] = {value: pseudo for pseudo, value in pseudonym_map.items()}
        
        return data
    
    def _apply_noise_addition(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply noise addition anonymization."""
        field_name = rule.field_name
        noise_scale = rule.parameters.get('noise_scale', 0.1)
        distribution = rule.parameters.get('distribution', 'gaussian')
        
        if rule.data_type == DataType.NUMERICAL:
            original_values = data[field_name].values
            
            if distribution == 'gaussian':
                noise = np.random.normal(0, noise_scale * np.std(original_values), len(original_values))
            elif distribution == 'laplace':
                noise = np.random.laplace(0, noise_scale * np.std(original_values), len(original_values))
            else:
                noise = np.random.uniform(-noise_scale, noise_scale, len(original_values))
            
            data[field_name] = original_values + noise
            
            # Ensure non-negative values if required
            if rule.parameters.get('non_negative', False):
                data[field_name] = np.maximum(data[field_name], 0)
        
        return data
    
    def _apply_shuffling(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply shuffling anonymization."""
        field_name = rule.field_name
        
        # Shuffle the values in the column
        shuffled_values = data[field_name].sample(frac=1).reset_index(drop=True)
        data[field_name] = shuffled_values.values
        
        return data
    
    def _apply_substitution(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply substitution anonymization."""
        field_name = rule.field_name
        substitution_map = rule.parameters.get('substitution_map', {})
        default_value = rule.parameters.get('default_value', 'UNKNOWN')
        
        if substitution_map:
            data[field_name] = data[field_name].map(substitution_map).fillna(default_value)
        else:
            # Generate synthetic substitutions
            unique_values = data[field_name].unique()
            if rule.data_type == DataType.CATEGORICAL:
                # Generate random categories
                categories = [f"CAT_{i:03d}" for i in range(len(unique_values))]
                sub_map = dict(zip(unique_values, categories))
                data[field_name] = data[field_name].map(sub_map)
            elif rule.data_type == DataType.TEXT:
                # Generate random text
                def generate_text(length=8):
                    return ''.join(random.choices(string.ascii_uppercase, k=length))
                
                sub_map = {val: generate_text() for val in unique_values}
                data[field_name] = data[field_name].map(sub_map)
        
        return data
    
    def _apply_differential_privacy(self, data: pd.DataFrame, rule: AnonymizationRule) -> pd.DataFrame:
        """Apply differential privacy mechanism."""
        field_name = rule.field_name
        epsilon = rule.parameters.get('epsilon', self.config.epsilon)
        mechanism = rule.parameters.get('mechanism', 'laplace')
        
        if rule.data_type == DataType.NUMERICAL:
            sensitivity = rule.parameters.get('sensitivity', 1.0)
            
            if mechanism == 'laplace':
                # Laplace mechanism
                scale = sensitivity / epsilon
                noise = np.random.laplace(0, scale, len(data))
                data[field_name] = data[field_name] + noise
            
            elif mechanism == 'gaussian':
                # Gaussian mechanism
                delta = rule.parameters.get('delta', self.config.delta)
                sigma = (sensitivity * np.sqrt(2 * np.log(1.25 / delta))) / epsilon
                noise = np.random.normal(0, sigma, len(data))
                data[field_name] = data[field_name] + noise
        
        return data
    
    def _enforce_k_anonymity(self, data: pd.DataFrame, rules: List[AnonymizationRule]) -> pd.DataFrame:
        """Enforce k-anonymity constraint."""
        k = self.config.k_anonymity
        
        # Identify quasi-identifiers
        quasi_identifiers = [
            rule.field_name for rule in rules 
            if rule.data_type == DataType.QUASI_IDENTIFIER
        ]
        
        if not quasi_identifiers:
            return data
        
        # Group by quasi-identifiers and count
        groups = data.groupby(quasi_identifiers).size()
        
        # Identify groups with fewer than k records
        small_groups = groups[groups < k]
        
        if len(small_groups) == 0:
            return data
        
        # Remove records in small groups (suppression)
        for group_values in small_groups.index:
            if isinstance(group_values, tuple):
                mask = pd.Series([True] * len(data))
                for i, qi in enumerate(quasi_identifiers):
                    mask &= (data[qi] == group_values[i])
            else:
                mask = (data[quasi_identifiers[0]] == group_values)
            
            data = data[~mask]
        
        logger.info(f"K-anonymity enforced: removed {len(small_groups)} small groups")
        return data
    
    def _enforce_l_diversity(self, data: pd.DataFrame, rules: List[AnonymizationRule]) -> pd.DataFrame:
        """Enforce l-diversity constraint."""
        l = self.config.l_diversity
        
        # Identify quasi-identifiers and sensitive attributes
        quasi_identifiers = [
            rule.field_name for rule in rules 
            if rule.data_type == DataType.QUASI_IDENTIFIER
        ]
        sensitive_attrs = [
            rule.field_name for rule in rules 
            if rule.data_type == DataType.SENSITIVE
        ]
        
        if not quasi_identifiers or not sensitive_attrs:
            return data
        
        # Check l-diversity for each sensitive attribute
        for sensitive_attr in sensitive_attrs:
            groups = data.groupby(quasi_identifiers)[sensitive_attr].apply(lambda x: x.nunique())
            
            # Identify groups with fewer than l distinct sensitive values
            non_diverse_groups = groups[groups < l]
            
            if len(non_diverse_groups) > 0:
                # Remove records in non-diverse groups
                for group_values in non_diverse_groups.index:
                    if isinstance(group_values, tuple):
                        mask = pd.Series([True] * len(data))
                        for i, qi in enumerate(quasi_identifiers):
                            mask &= (data[qi] == group_values[i])
                    else:
                        mask = (data[quasi_identifiers[0]] == group_values)
                    
                    data = data[~mask]
                
                logger.info(f"L-diversity enforced for {sensitive_attr}: removed {len(non_diverse_groups)} groups")
        
        return data
    
    def _calculate_utility_score(self, original: pd.DataFrame, anonymized: pd.DataFrame) -> float:
        """Calculate utility score comparing original and anonymized data."""
        try:
            if len(anonymized) == 0:
                return 0.0
            
            # Record preservation ratio
            record_ratio = len(anonymized) / len(original)
            
            # Calculate information loss for numerical columns
            numerical_cols = original.select_dtypes(include=[np.number]).columns
            info_loss = 0.0
            
            for col in numerical_cols:
                if col in anonymized.columns:
                    orig_var = original[col].var()
                    anon_var = anonymized[col].var()
                    if orig_var > 0:
                        info_loss += abs(orig_var - anon_var) / orig_var
            
            # Normalize information loss
            if len(numerical_cols) > 0:
                info_loss = info_loss / len(numerical_cols)
            
            # Combine metrics (higher is better)
            utility_score = record_ratio * (1 - min(info_loss, 1.0))
            return max(0.0, min(1.0, utility_score))
            
        except Exception as e:
            logger.error(f"Utility score calculation failed: {e}")
            return 0.5  # Default neutral score
    
    def _calculate_privacy_score(self, data: pd.DataFrame, rules: List[AnonymizationRule]) -> float:
        """Calculate privacy score based on anonymization strength."""
        try:
            if len(data) == 0:
                return 1.0  # Perfect privacy (no data)
            
            score = 0.0
            total_weight = 0.0
            
            # Weight different anonymization methods
            method_weights = {
                AnonymizationMethod.SUPPRESSION: 0.9,
                AnonymizationMethod.GENERALIZATION: 0.7,
                AnonymizationMethod.PSEUDONYMIZATION: 0.8,
                AnonymizationMethod.NOISE_ADDITION: 0.6,
                AnonymizationMethod.SHUFFLING: 0.5,
                AnonymizationMethod.SUBSTITUTION: 0.8,
                AnonymizationMethod.DIFFERENTIAL_PRIVACY: 1.0
            }
            
            for rule in rules:
                weight = method_weights.get(rule.method, 0.5)
                
                # Adjust weight based on data type sensitivity
                if rule.data_type == DataType.SENSITIVE:
                    weight *= 1.2
                elif rule.data_type == DataType.IDENTIFIER:
                    weight *= 1.1
                
                score += weight
                total_weight += 1.0
            
            # Normalize score
            if total_weight > 0:
                score = score / total_weight
            
            # Adjust for k-anonymity and l-diversity
            if self.config.k_anonymity > 1:
                score *= (1 + 0.1 * (self.config.k_anonymity - 1))
            if self.config.l_diversity > 1:
                score *= (1 + 0.1 * (self.config.l_diversity - 1))
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Privacy score calculation failed: {e}")
            return 0.5  # Default neutral score
    
    def _determine_anonymization_level(self, rules: List[AnonymizationRule]) -> str:
        """Determine the overall anonymization level."""
        method_counts = Counter(rule.method for rule in rules)
        
        if AnonymizationMethod.DIFFERENTIAL_PRIVACY in method_counts:
            return "HIGH"
        elif (AnonymizationMethod.PSEUDONYMIZATION in method_counts or 
              AnonymizationMethod.SUPPRESSION in method_counts):
            return "MEDIUM"
        elif (AnonymizationMethod.GENERALIZATION in method_counts or
              AnonymizationMethod.NOISE_ADDITION in method_counts):
            return "LOW"
        else:
            return "MINIMAL"
    
    def _estimate_memory_usage(self, data: pd.DataFrame) -> float:
        """Estimate memory usage of DataFrame in MB."""
        try:
            memory_bytes = data.memory_usage(deep=True).sum()
            return memory_bytes / (1024 * 1024)  # Convert to MB
        except:
            return 0.0
    
    def reverse_pseudonymization(self, data: pd.DataFrame, field_name: str, 
                                key_id: str) -> pd.DataFrame:
        """Reverse pseudonymization if possible."""
        try:
            cache_key = f"{field_name}_{key_id}"
            
            if cache_key not in self.pseudonym_cache:
                logger.warning(f"No reversible pseudonymization found for {field_name}")
                return data
            
            reverse_map = self.pseudonym_cache[cache_key]
            data[field_name] = data[field_name].map(reverse_map).fillna(data[field_name])
            
            logger.info(f"Pseudonymization reversed for field: {field_name}")
            return data
            
        except Exception as e:
            logger.error(f"Reverse pseudonymization failed: {e}")
            return data
    
    def create_anonymization_rules(self, data: pd.DataFrame, 
                                 sensitive_fields: List[str] = None,
                                 identifier_fields: List[str] = None,
                                 quasi_identifier_fields: List[str] = None) -> List[AnonymizationRule]:
        """Automatically create anonymization rules based on data analysis."""
        rules = []
        
        sensitive_fields = sensitive_fields or []
        identifier_fields = identifier_fields or []
        quasi_identifier_fields = quasi_identifier_fields or []
        
        for column in data.columns:
            # Determine data type
            if data[column].dtype in ['int64', 'float64']:
                data_type = DataType.NUMERICAL
                method = AnonymizationMethod.NOISE_ADDITION
                params = {'noise_scale': 0.05}
            elif data[column].dtype == 'object':
                if column in identifier_fields:
                    data_type = DataType.IDENTIFIER
                    method = AnonymizationMethod.PSEUDONYMIZATION
                    params = {}
                elif column in sensitive_fields:
                    data_type = DataType.SENSITIVE
                    method = AnonymizationMethod.GENERALIZATION
                    params = {'level': 2}
                elif column in quasi_identifier_fields:
                    data_type = DataType.QUASI_IDENTIFIER
                    method = AnonymizationMethod.GENERALIZATION
                    params = {'level': 1}
                else:
                    data_type = DataType.CATEGORICAL
                    method = AnonymizationMethod.SUBSTITUTION
                    params = {}
            else:
                data_type = DataType.TEXT
                method = AnonymizationMethod.GENERALIZATION
                params = {'max_length': 10}
            
            # Adjust method based on uniqueness
            unique_ratio = data[column].nunique() / len(data)
            if unique_ratio > 0.9:  # High uniqueness suggests identifier
                if data_type != DataType.IDENTIFIER:
                    method = AnonymizationMethod.PSEUDONYMIZATION
            elif unique_ratio < 0.1:  # Low uniqueness suggests categorical
                method = AnonymizationMethod.SHUFFLING
            
            rule = AnonymizationRule(
                field_name=column,
                data_type=data_type,
                method=method,
                parameters=params
            )
            rules.append(rule)
        
        return rules
    
    def cleanup(self):
        """Clean up anonymizer cache and temporary data."""
        try:
            with self.lock:
                # Clear large cache entries
                cache_size = sum(len(str(v)) for v in self.pseudonym_cache.values())
                if cache_size > self.memory_limit_mb * 1024 * 1024 * 0.8:  # 80% of limit
                    # Keep only most recently used entries
                    keys_to_remove = list(self.pseudonym_cache.keys())[:-100]  # Keep last 100
                    for key in keys_to_remove:
                        del self.pseudonym_cache[key]
                
                # Clear old keys (keep only last 50)
                if len(self.keys) > 50:
                    old_keys = list(self.keys.keys())[:-50]
                    for key in old_keys:
                        del self.keys[key]
            
            self.stats['last_cleanup'] = time.time()
            logger.info("Data anonymizer cleanup completed")
            
        except Exception as e:
            logger.error(f"Anonymizer cleanup failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get anonymizer statistics."""
        return {
            **self.stats,
            'cache_size': len(self.pseudonym_cache),
            'keys_stored': len(self.keys),
            'memory_usage_mb': self._estimate_current_memory_usage()
        }
    
    def _estimate_current_memory_usage(self) -> float:
        """Estimate current memory usage of anonymizer."""
        try:
            cache_size = sum(len(str(v)) for v in self.pseudonym_cache.values())
            keys_size = sum(len(k) for k in self.keys.values())
            return (cache_size + keys_size) / (1024 * 1024)  # Convert to MB
        except:
            return 0.0
