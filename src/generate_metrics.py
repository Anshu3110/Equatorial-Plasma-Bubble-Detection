import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
import os

# Configuration
RESULTS_FILE = "results/validation_results.csv"
OUTPUT_DIR = "results/metrics"

def generate_metrics():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    if not os.path.exists(RESULTS_FILE):
        print(f"Error: {RESULTS_FILE} not found. Run validation first.")
        return
        
    df = pd.read_csv(RESULTS_FILE)
    
    y_true = df['ground_truth_gnss']
    y_pred = df['prediction_ai']
    
    # Filter out 'Unknown' GNSS labels if any (Label -1)
    valid_mask = y_true != -1
    y_true = y_true[valid_mask]
    y_pred = y_pred[valid_mask]
    df_valid = df[valid_mask]
    
    print(f"Generating metrics on {len(df_valid)} valid samples...")
    
    # 1. quantitative Metrics
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=['Clear', 'EPB'])
    
    print("\nClassification Report:")
    print(report)
    
    # Save text report
    with open(os.path.join(OUTPUT_DIR, "metrics_report.txt"), "w") as f:
        f.write(f"Accuracy: {acc:.4f}\n\n")
        f.write(report)
        
    # 2. Confusion Matrix Plot
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Clear', 'EPB'], yticklabels=['Clear', 'EPB'])
    plt.title('Confusion Matrix (AI vs GNSS)')
    plt.xlabel('Predicted (AI)')
    plt.ylabel('Actual (GNSS)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"))
    plt.close()
    print("Saved confusion_matrix.png")
    
    # 3. Correlation Scatter Plot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df_valid, x='mse', y='gnss_max_roti', hue='prediction_ai', palette={0:'blue', 1:'red'})
    plt.title('Correlation: Model Error (MSE) vs Ionospheric Activity (ROTI)')
    plt.xlabel('AI Reconstruction Error (MSE)')
    plt.ylabel('GNSS Activity Index (ROTI)')
    plt.axvline(x=0.035, color='gray', linestyle='--', label='AI Threshold')
    plt.axhline(y=5.0, color='gray', linestyle=':', label='GNSS Threshold')
    plt.legend(title="AI Prediction")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "correlation_plot.png"))
    plt.close()
    print("Saved correlation_plot.png")

if __name__ == "__main__":
    generate_metrics()
