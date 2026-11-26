# tasks/04_shape_model.md
Objective: one LightGBM per zone on per-unit hourly load.
Target: load_mw / (base_gwh-scaled size_idx of that year), Uri excluded.
Features: temp_f_popwt, temp_f_avg24, temp_f_ewm3d, dewpoint_f_popwt,
hour, month, weekday, holiday. NOTHING date-indexed.
CV: group by year (leave-one-year-out) to avoid leakage; light tuning
only (num_leaves, min_data_in_leaf, learning_rate).
Accept: LOYO hourly MAPE ≤ 5% per zone; partial-dependence on temp is
monotone above ~78°F; saved model + feature list versioned.
