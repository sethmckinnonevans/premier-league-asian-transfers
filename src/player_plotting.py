import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go


def plot_players(df, 
                 positions, 
                 x_metric, 
                 y_metric, 
                 title, 
                 x_label, 
                 y_label, 
                 kit_colours, 
                 leagues=None, 
                 seasons=None, 
                 nationalities=None):

    filtered_df = df.copy()

    if leagues is not None:
        filtered_df = filtered_df[filtered_df["league"].isin(leagues)]

    if seasons is not None:
        filtered_df = filtered_df[filtered_df["season"].isin(seasons)]

    if nationalities is not None:
        filtered_df = filtered_df[filtered_df["country"].isin(nationalities)]

    if positions is not None:
        filtered_df = filtered_df[filtered_df["scoutingPosition"].isin(positions)]

    filtered_df = filtered_df[
        filtered_df["eligible"].eq(True)
    ].dropna(subset=[x_metric, y_metric, "team id", "name"])

    if filtered_df.empty:
        raise ValueError("No eligible players match these filters.")

    point_colours = filtered_df["team id"].map(kit_colours).fillna("#CCCCCC")

    plt.rcParams["font.family"] = "DIN Alternate"

    plot_x = filtered_df[x_metric]
    plot_y = filtered_df[y_metric]

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.patch.set_facecolor("#404040")
    ax.set_facecolor("#404040")

    ax.scatter(plot_x, plot_y, c=point_colours, s=150)

    ax.set_xlabel(x_label, fontsize=12, color="#CCCCCC")
    ax.set_ylabel(y_label, fontsize=12, color="#CCCCCC")
    ax.set_title(title, fontsize=16, color="#CCCCCC", loc="left")

    ax.tick_params(axis="both", colors="#CCCCCC", labelsize=12)

    for spine in ax.spines.values():
        spine.set_color("#CCCCCC")

    for _, row in filtered_df.iterrows():
        ax.annotate(
            row["name"],
            (row[x_metric], row[y_metric]),
            xytext=(0, -18),
            textcoords="offset points",
            ha="center",
            color="#CCCCCC",
            fontsize=10
        )

    fig.tight_layout()

    return fig, ax




radar_metrics = {
    "Centreback": {
        "Passing": [
            "accuratePasses_per90",
            "accurateOppositionHalfPasses_per90",
            "accuratePassesPercentage",
            "accurateLongBalls_per90",
            "accurateLongBallsPercentage",
        ],
        "Aerial": [
            "aerialDuelsWon_per90",
            "aerialDuelsWonPercentage",
        ],
        "Ground Duels": [
            "groundDuelsWon_per90",
            "groundDuelsWonPercentage",
            "dribbledPast_per90",
        ],
        "Defending": [
            "ballRecovery_per90",
            "blockedShots_per90",
            "clearances_per90",
            "interceptions_per90",
            "tacklesWon_per90",
            "tacklesWonPercentage",
        ],
        "Security": [
            "dispossessed_per90",
            "errorLeadToShot_per90",
        ],
        "Attacking": [
            "goals_per90",
            "expectedGoals_per90",
        ],
    },

    "Fullback": {
        "Passing": [
            "accuratePasses_per90",
            "accurateFinalThirdPasses_per90",
            "accuratePassesPercentage",
        ],
        "Aerial": [
            "aerialDuelsWon_per90",
            "aerialDuelsWonPercentage",
        ],
        "Ground Duels": [
            "groundDuelsWon_per90",
            "groundDuelsWonPercentage",
            "dribbledPast_per90",
        ],
        "Defending": [
            "ballRecovery_per90",
            "blockedShots_per90",
            "clearances_per90",
            "interceptions_per90",
            "tacklesWon_per90",
            "tacklesWonPercentage",
        ],
        "Crossing": [
            "accurateCrosses_per90",
            "accurateCrossesPercentage",
        ],
        "Creativity": [
            "assists_per90",
            "expectedAssists_per90",
            "keyPasses_per90",
        ],
    },

    "Midfielder": {
        "Passing": [
            "accuratePasses_per90",
            "accurateFinalThirdPasses_per90",
            "accuratePassesPercentage",
            "accurateLongBalls_per90",
            "accurateLongBallsPercentage",
            "touches_per90",
        ],
        "Aerial": [
            "aerialDuelsWon_per90",
            "aerialDuelsWonPercentage",
        ],
        "Defending": [
            "ballRecovery_per90",
            "clearances_per90",
            "interceptions_per90",
            "tacklesWon_per90",
            "tacklesWonPercentage",
            "possessionWonAttThird_per90",
        ],
        "Creativity": [
            "assists_per90",
            "expectedAssists_per90",
            "keyPasses_per90",
            "bigChancesCreated_per90",
            "passToAssist_per90",
            "successfulDribbles_per90",
            "successfulDribblesPercentage",
        ],
        "Attacking": [
            "goals_per90",
            "expectedGoals_per90",
            "shotsOnTarget_per90",
        ],
    },

    "Winger": {
        "Dribbling": [
            "successfulDribbles_per90",
            "successfulDribblesPercentage",
            "wasFouled_per90",
        ],
        "Passing": [
            "accuratePasses_per90",
            "accurateFinalThirdPasses_per90",
            "accuratePassesPercentage",
            "accurateCrosses_per90",
            "accurateCrossesPercentage",
            "touches_per90",
        ],
        "Creativity": [
            "assists_per90",
            "expectedAssists_per90",
            "keyPasses_per90",
            "bigChancesCreated_per90",
            "passToAssist_per90",
        ],
        "Attacking": [
            "goals_per90",
            "expectedGoals_per90",
            "shotsOnTarget_per90",
            "goalConversionPercentage",
        ],
        "Defending": [
            "ballRecovery_per90",
            "interceptions_per90",
            "tacklesWon_per90",
            "tacklesWonPercentage",
            "possessionWonAttThird_per90",
        ],
    },

    "Striker": {
        "Attacking": [
            "goals_per90",
            "expectedGoals_per90",
            "shotsOnTarget_per90",
            "goalConversionPercentage",
        ],
        "Creativity": [
            "assists_per90",
            "expectedAssists_per90",
            "keyPasses_per90",
            "bigChancesCreated_per90",
            "passToAssist_per90",
        ],
        "Passing": [
            "accuratePasses_per90",
            "accurateFinalThirdPasses_per90",
            "accuratePassesPercentage",
            "touches_per90",
        ],
        "Aerial": [
            "aerialDuelsWon_per90",
            "aerialDuelsWonPercentage",
        ],
        "Defending": [
            "ballRecovery_per90",
            "interceptions_per90",
            "tacklesWon_per90",
            "tacklesWonPercentage",
            "possessionWonAttThird_per90",
        ],
        "Dribbling": [
            "successfulDribbles_per90",
            "successfulDribblesPercentage",
            "wasFouled_per90",
        ],
    },

    "Goalkeeper": {
        "Shot Stopping": [
            "saves_per90",
            "savePercentage",
            "savedShotsFromInsideTheBox_per90",
            "savedShotsFromOutsideTheBox_per90",
            "goalsConceded_per90",
            "cleanSheet",
            "penaltySavePercentage",
        ],
        "Area Command": [
            "highClaims_per90",
            "punches_per90",
            "successfulRunsOut_per90",
        ],
        "Distribution": [
            "accurateLongBalls_per90",
            "accurateLongBallsPercentage",
            "accuratePasses_per90",
            "accuratePassesPercentage",
        ],
    },
}

radar_metric_labels = {
    # Passing
    "accuratePasses_per90": "Passes Completed / 90",
    "accurateFinalThirdPasses_per90": "Final Third Passes / 90",
    "accurateOppositionHalfPasses_per90": "Opposition Half Passes / 90",
    "accuratePassesPercentage": "Passing Accuracy %",
    "accurateLongBalls_per90": "Long Balls Completed / 90",
    "accurateLongBallsPercentage": "Long Ball Accuracy %",
    "touches_per90": "Touches / 90",

    # Crossing
    "accurateCrosses_per90": "Crosses Completed / 90",
    "accurateCrossesPercentage": "Crossing Accuracy %",

    # Creativity
    "assists_per90": "Assists / 90",
    "expectedAssists_per90": "Expected Assists / 90",
    "keyPasses_per90": "Key Passes / 90",
    "bigChancesCreated_per90": "Big Chances Created / 90",
    "passToAssist_per90": "Passes Leading to Assists / 90",

    # Attacking
    "goals_per90": "Goals / 90",
    "expectedGoals_per90": "Expected Goals / 90",
    "shotsOnTarget_per90": "Shots on Target / 90",
    "goalConversionPercentage": "Shot Conversion %",

    # Dribbling
    "successfulDribbles_per90": "Successful Dribbles / 90",
    "successfulDribblesPercentage": "Dribble Success %",
    "wasFouled_per90": "Fouls Won / 90",

    # Aerial
    "aerialDuelsWon_per90": "Aerial Duels Won / 90",
    "aerialDuelsWonPercentage": "Aerial Duel Win Rate %",

    # Ground duels
    "groundDuelsWon_per90": "Ground Duels Won / 90",
    "groundDuelsWonPercentage": "Ground Duel Win Rate %",
    "dribbledPast_per90": "Dribbled Past / 90",

    # Defending
    "ballRecovery_per90": "Ball Recoveries / 90",
    "blockedShots_per90": "Shots Blocked / 90",
    "clearances_per90": "Clearances / 90",
    "interceptions_per90": "Interceptions / 90",
    "tacklesWon_per90": "Tackles Won / 90",
    "tacklesWonPercentage": "Tackling Success %",
    "possessionWonAttThird_per90": "Final Third Recoveries / 90",
    "dispossessed_per90": "Times Dispossessed / 90",
    "errorLeadToShot_per90": "Errors Leading to Shots / 90",

    # Goalkeeping
    "saves_per90": "Saves / 90",
    "savePercentage": "Save %",
    "savedShotsFromInsideTheBox_per90": "Inside-Box Saves / 90",
    "savedShotsFromOutsideTheBox_per90": "Outside-Box Saves / 90",
    "goalsConceded_per90": "Goals Conceded / 90",
    "penaltySavePercentage": "Penalty Save %",
    "highClaims_per90": "High Claims / 90",
    "punches_per90": "Punches / 90",
    "successfulRunsOut_per90": "Successful Runs Out / 90",
    "cleanSheet": "Clean Sheets"

}
    
def blend_colour(light_hex, dark_hex, percentile):
    p = np.clip(float(percentile) / 100, 0, 1)

    light = [int(light_hex[i:i + 2], 16) for i in (1, 3, 5)]
    dark = [int(dark_hex[i:i + 2], 16) for i in (1, 3, 5)]

    rgb = [
        round(a + (b - a) * p)
        for a, b in zip(light, dark)
    ]

    return "#" + "".join(f"{v:02X}" for v in rgb)


def plot_player_radar_interactive(df, player_name, season):

    # Find player
    player_df = df[
        df["name"].eq(player_name)
        & df["season"].eq(season)
    ]

    if player_df.empty:
        raise ValueError(
            f"No player found in {season} with name: {player_name}"
        )

    if len(player_df) > 1:
        raise ValueError(
            f"Multiple rows found for {player_name} in {season}. "
            "Filter by league or team to identify the correct player."
        )

    player = player_df.iloc[0]
    position = player["scoutingPosition"]

    if position not in radar_metrics:
        raise ValueError(f"No radar metrics defined for {position}")

    # Category-based metrics for this position
    position_categories = radar_metrics[position]

    # One blue gradient for every category
    light_blue = "#BBD7FC"
    dark_blue = "#095CC8"

    # Filter metrics, preserving category order
    valid_categories = {}
    for category, category_metrics in position_categories.items():

        valid_metrics = []

        for metric in category_metrics:
            percentile_col = f"{metric}_pctl"

            if percentile_col not in df.columns:
                continue

            value = player[percentile_col]

            if pd.notna(value) and np.isfinite(float(value)):
                valid_metrics.append(metric)

        if valid_metrics:
            valid_categories[category] = valid_metrics

    # Flatten metrics while retaining category information
    metrics = []
    metric_categories = []

    for category, category_metrics in valid_categories.items():
        metrics.extend(category_metrics)
        metric_categories.extend([category] * len(category_metrics))

    if len(metrics) < 3:
        raise ValueError(
            f"Fewer than 3 valid metrics for {player_name}"
        )

    percentiles = [
        float(player[f"{metric}_pctl"])
        for metric in metrics
    ]

    raw_values = [
        player[metric] if metric in df.columns else np.nan
        for metric in metrics
    ]

    labels = [radar_metric_labels.get(metric, metric) for metric in metrics]

    # Layout: metrics sit in the CENTRE of each angular slice
    category_gap = 10  # degrees between category groups
    
    n = len(metrics)
    n_categories = len(valid_categories)
    
    total_gap = category_gap * n_categories
    usable_angle = 360 - total_gap
    step = usable_angle / n
    
    angles = []
    current_angle = 0
    
    for category, category_metrics in valid_categories.items():
    
        for metric in category_metrics:
            # Put each metric halfway through its angular slice
            angles.append(current_angle + step / 2)
            current_angle += step
    
        # Leave a gap between categories
        current_angle += category_gap
    
    angle_lookup = dict(zip(metrics, angles))
    
    category_centres = {}

    for category, category_metrics in valid_categories.items():
        category_angles = [angle_lookup[m] for m in category_metrics]
        category_centres[category] = (
            category_angles[0] + category_angles[-1]
        ) / 2

    # Correct starting angle and calculate category centres
    angle_lookup = dict(zip(metrics, angles))
    category_centres = {}

    for category, category_metrics in valid_categories.items():
        category_angles = [angle_lookup[m] for m in category_metrics]
        category_centres[category] = (
            category_angles[0] + category_angles[-1]
        ) / 2

    fig = go.Figure()

    # Draw individual hoverable wedges without marker points
    for i, (metric, percentile) in enumerate(zip(metrics, percentiles)):
    
        category = metric_categories[i]
        half_width = step / 2
    
        start_angle = angles[i] - half_width
        end_angle = angles[i] + half_width
    
        colour = blend_colour(light_blue, dark_blue, percentile)
    
        raw = raw_values[i]
        raw_text = f"{raw:.2f}" if pd.notna(raw) else "Unavailable"
    
        hover_text = (
            f"<b>{labels[i]}</b><br>"
            f"Category: {category}<br>"
            f"Percentile: {percentile:.1f}<br>"
            f"Raw value: {raw_text}"
        )
        
        fig.add_trace(go.Scatterpolar(
            r=[0, percentile, percentile, 0],
            theta=[start_angle, start_angle, end_angle, end_angle],
            mode="none",
            fill="toself",
            fillcolor=colour,
            line=dict(width=0),
            hoverinfo="skip",           
            showlegend=False
        ))

         # Invisible hover target with custom tooltip
        fig.add_trace(go.Scatterpolar(
            r=[percentile / 2],
            theta=[angles[i]],
            mode="markers",
            marker=dict(
                size=25,
                color="rgba(0,0,0,0)",
                line=dict(width=0)
            ),
            name=labels[i],
            customdata=[[
                labels[i],
                category,
                percentile,
                raw_text
            ]],
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>Category: %{customdata[1]}"
                "<br>Percentile: %{customdata[2]:.1f}"
                "<br>Raw value: %{customdata[3]}"
                "<extra></extra>"
            ),

            hoverlabel=dict(
                bgcolor="#505050",
                bordercolor="#CCCCCC",
                font=dict(
                    family="DIN Alternate",
                    size=12,
                    color="#FFFFFF"
                ),
                align="left"
            ),
            showlegend=False
        ))

    # Category labels positioned around the outside
    annotations = []

    for category, centre in category_centres.items():
        annotations.append(dict(
            text=f"<b>{category}</b>",
            x=0.5 + 0.6 * np.sin(np.radians(centre)),
            y=0.5 + 0.6 * np.cos(np.radians(centre)),
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=10, color="#EEEEEE"),
            xanchor="center",
            yanchor="middle"
        ))
        
    fig.update_layout(
        title=dict(
            text=f"{player_name} - {player["team"]} {season}",
            x=0.5,
            font=dict(size=16, color="#FFFFFF")
        ),
        paper_bgcolor="#404040",
        plot_bgcolor="#404040",
        font=dict(
            family="DIN Alternate",
            color="#CCCCCC"
        ),
        polar=dict(
            bgcolor="#404040",
            radialaxis=dict(
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                tickfont=dict(size=8, color="#CCCCCC"),
                gridcolor="#666666",
                linecolor="#888888"
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=angles,
                ticktext=labels,
                tickfont=dict(size=10, color="#CCCCCC"),
                gridcolor="#777777",
                linecolor="#888888",
                rotation=90,
                direction="clockwise"
            )
        ),

        showlegend=False,
        autosize = True,
        height=None,
        margin=dict(l=100, r=100, t=100, b=100),


    )

    return fig









    