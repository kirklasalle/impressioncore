#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/training/aggregate_grid_search_results.py #training
**Category:** Training System
**Status:** Active
"""









# Aggregate Grid Search Results

# Created:** October 15, 2024
# Updated:** August 4, 2025
# Author:** ImpressionCore Team
# Tags:** #python #source_code #src\\training\\aggregate_grid_search_results.py #training
# Category:** Training System
# Status:** Active

"""
Aggregate and summarize grid search results for B2 training.

- Scans the output directory for per-class metrics and confusion matrix CSVs.
- Aggregates results by hyperparameter set (parsed from directory or log).
- Reports best runs by macro F1 (sentiment/intent), per-class F1, and confusion matrix stats.
- Prints summary table and saves to summary CSV.

Usage:
    python aggregate_grid_search_results.py --results-dir <output_dir>
"""
import os
import glob
import pandas as pd
import re
import argparse

def parse_params_from_path(path):
    # Try to extract params from directory or file name
    # Example: 'Train_Sentiment_per_class_metrics_epoch_1.csv' or 'grid_loss0.2_intent0.5_drop0.3_lr2.0_epoch1.csv'
    m = re.search(r'loss_weight_sentiment([\d.]+).*loss_weight_intent([\d.]+).*dropout([\d.]+).*head_lr_multiplier([\d.]+)', path)
    if m:
        return {
            'loss_weight_sentiment': float(m.group(1)),
            'loss_weight_intent': float(m.group(2)),
            'dropout': float(m.group(3)),
            'head_lr_multiplier': float(m.group(4)),
        }
    return {}

def aggregate_results(results_dir):
    summary = []
    for csv_path in glob.glob(os.path.join(results_dir, '*per_class_metrics_epoch_*.csv')):
        df = pd.read_csv(csv_path, index_col=0)
        params = parse_params_from_path(csv_path)
        # Get macro F1 for sentiment/intent
        if 'S0' in df.index:
            macro_f1 = df.loc[['S0','S1','S2'],'f1-score'].mean()
            tag = 'Sentiment'
        elif 'I0' in df.index:
            macro_f1 = df.loc[[f'I{i}' for i in range(10)],'f1-score'].mean()
            tag = 'Intent'
        else:
            continue
        epoch = int(re.search(r'epoch_(\d+)', csv_path).group(1))
        summary.append({
            'file': os.path.basename(csv_path),
            'tag': tag,
            'epoch': epoch,
            'macro_f1': macro_f1,
            # params
        })
    summary_df = pd.DataFrame(summary)
    if not summary_df.empty:
        best_sentiment = summary_df[summary_df['tag']=='Sentiment'].sort_values('macro_f1', ascending=False).head(1)
        best_intent = summary_df[summary_df['tag']=='Intent'].sort_values('macro_f1', ascending=False).head(1)
        print('Best Sentiment Macro F1:')
        print(best_sentiment)
        print('Best Intent Macro F1:')
        print(best_intent)
        summary_df.to_csv(os.path.join(results_dir, 'grid_search_summary.csv'), index=False)
        print(f"[Summary] Saved grid search summary to {os.path.join(results_dir, 'grid_search_summary.csv')}")
    else:
        print('No per-class metrics found.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', type=str, required=True, help='Directory with grid search results')
    args = parser.parse_args()
    aggregate_results(args.results_dir)
