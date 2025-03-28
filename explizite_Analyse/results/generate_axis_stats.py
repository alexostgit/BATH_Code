import pandas as pd
import os
import matplotlib.pyplot as plt

def create_axis_csvs_and_print_tables():
    run = 'combined'
    # Path to the input CSV file
    input_csv = f"explizite_Analyse/results/results_{run}/results_{run}.csv"
    
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Check if the Axis column exists
    if 'Axis Name' not in df.columns:
        raise ValueError("The CSV file does not contain an 'Axis' column.")
    unique_axes = sorted(df['Axis Name'].unique())

    # Ensure the needed columns exist
    for col in ['Model', 'Group', 'mean', 'SEM']:
        if col not in df.columns:
            raise ValueError(f"The CSV file must contain a '{col}' column.")

    # Create output directories
    output_dir = f"explizite_Analyse/results/results_{run}"
    output_dir_heatmaps = os.path.join(output_dir, f"heatmaps_{run}")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir_heatmaps, exist_ok=True)

    for axis in unique_axes:
        # Filter rows for the current axis
        axis_df = df[df['Axis Name'] == axis].copy()

        # Combine mean and SEM into 'X.XX±Y.YY'
        axis_df['Mean±SEM'] = (
            axis_df['mean'].round(2).astype(str) + "±" +
            axis_df['SEM'].round(2).astype(str)
        )

        # Pivot for Mean±SEM text display
        pivot_df = axis_df.pivot(index='Model', columns='Group', values='Mean±SEM')

        # Save pivot table to CSV
        output_csv = os.path.join(output_dir, f"axis_{axis}.csv")
        pivot_df.to_csv(output_csv)

        # Pivot for numeric heatmap
        pivot_numeric_df = axis_df.pivot(index='Model', columns='Group', values='mean')

        # Calculate averages for the columns and rows
        col_avgs = pivot_numeric_df.mean(axis=0)
        row_avgs = pivot_numeric_df.mean(axis=1)
        # Calculate standard deviations for the columns and rows
        col_stds = pivot_numeric_df.std(axis=0)
        row_stds = pivot_numeric_df.std(axis=1)
        # Calculate a minimal height so it roughly fits only the text
        # and a minimal width so columns don’t get squashed:
        fig_width = max(4.0, pivot_numeric_df.shape[1] * 1.2)
        fig_height = max(1.0, pivot_numeric_df.shape[0] * 0.5)
        
        # Create figure/axes for the heatmap
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        # Plot the heatmap using the numeric means
        if axis == 'Bedrohungswahrnehmung':
            cax = ax.imshow(pivot_numeric_df, cmap='Reds', aspect='auto', vmin=25)
        else:
            cax = ax.imshow(pivot_numeric_df, cmap='Blues', aspect='auto', vmin=75)

        # Add a colorbar (shrunken a bit to keep it tight)
        cb = fig.colorbar(cax, ax=ax, fraction=0.05, pad=0.05)
        cb.set_label('Durchschnittswert', rotation=90)

        # Set tick labels
        ax.set_xticks(range(len(pivot_numeric_df.columns)))
        ax.set_yticks(range(len(pivot_numeric_df.index)))

        # Update tick labels to include averages (Ø) and standard deviations (σ)
        new_xticklabels = [f"{col}\nØ {col_avgs[col]:.2f} ± {col_stds[col]:.2f}" 
                           for col in pivot_numeric_df.columns]
        new_yticklabels = [f"{model}\nØ {row_avgs[model]:.2f} ± {row_stds[model]:.2f}" 
                           for model in pivot_numeric_df.index]
        ax.set_xticklabels(new_xticklabels, rotation=0, ha='center', fontsize=6)
        ax.set_yticklabels(new_yticklabels, fontsize=6)
        
        # Title
        ax.set_title(f"{axis} (Durchschnitts-Score ± Stand. Abw. vom Mittelwert)", pad=10)

        # Overlay each cell with the Mean±SEM text
        for i in range(pivot_numeric_df.shape[0]):      # for each row
            for j in range(pivot_numeric_df.shape[1]):  # for each column
                text_val = pivot_df.iat[i, j]  # e.g. "2.45±0.23"
                ax.text(j, i, text_val,
                        ha='center', va='center', color='black', fontsize=8)

        # Make layout tight
        plt.tight_layout()

        # Save the figure
        heatmap_file = os.path.join(output_dir_heatmaps, f"axis_{axis}_heatmap.png")
        plt.savefig(heatmap_file, dpi=150, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    create_axis_csvs_and_print_tables()