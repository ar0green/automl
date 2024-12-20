from backend.src.pipeline import run_pipeline

if __name__ == "__main__":

    data_path = 'data/iris/iris.data'
    column_names = [
        'sepal_length',
        'sepal_width',
        'petal_length',
        'petal_width',
        'species'
    ]
    target_column = 'species'
    task_type = 'classification'
    sep = ','
    dataset_name = 'iris'

    run_pipeline(
        data_path, column_names, target_column,
        task_type=task_type, sep=sep, dataset_name=dataset_name,
    )

    # # Пример для Mushroom датасета
    # data_path = 'data/mushroom/mushroom.data'
    # column_names = [
    #     'class',
    #     'cap-shape',
    #     'cap-surface',
    #     'cap-color',
    #     'bruises',
    #     'odor',
    #     'gill-attachment',
    #     'gill-spacing',
    #     'gill-size',
    #     'gill-color',
    #     'stalk-shape',
    #     'stalk-root',
    #     'stalk-surface-above-ring',
    #     'stalk-surface-below-ring',
    #     'stalk-color-above-ring',
    #     'stalk-color-below-ring',
    #     'veil-type',
    #     'veil-color',
    #     'ring-number',
    #     'ring-type',
    #     'spore-print-color',
    #     'population',
    #     'habitat'
    # ]
    # target_column = 'class'
    # task_type = 'classification'
    # sep = ','
    # dataset_name = 'mushroom'

    # run_pipeline(
    #     data_path, column_names, target_column,
    #     task_type=task_type, sep=sep, dataset_name=dataset_name
    # )

    data_path = 'data/breast_cancer/wdbc.data'
    column_names = [
        'id',
        'diagnosis',
        'radius_mean',
        'texture_mean',
        'perimeter_mean',
        'area_mean',
        'smoothness_mean',
        'compactness_mean',
        'concavity_mean',
        'concave_points_mean',
        'symmetry_mean',
        'fractal_dimension_mean',
        'radius_se',
        'texture_se',
        'perimeter_se',
        'area_se',
        'smoothness_se',
        'compactness_se',
        'concavity_se',
        'concave_points_se',
        'symmetry_se',
        'fractal_dimension_se',
        'radius_worst',
        'texture_worst',
        'perimeter_worst',
        'area_worst',
        'smoothness_worst',
        'compactness_worst',
        'concavity_worst',
        'concave_points_worst',
        'symmetry_worst',
        'fractal_dimension_worst'
    ]
    target_column = 'diagnosis'
    task_type = 'classification'
    sep = ','
    dataset_name = 'breast_cancer_model'

    run_pipeline(
        data_path, column_names, target_column,
        task_type=task_type, sep=sep, dataset_name=dataset_name
    )

    data_path = 'data/boston.csv'
    column_names = None
    target_column = 'medv'
    task_type = 'regression'
    sep = ','
    dataset_name = 'boston_housing'

    run_pipeline(
        data_path, column_names, target_column,
        task_type=task_type, sep=sep, dataset_name=dataset_name
    )