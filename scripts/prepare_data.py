import pandas as pd
from sklearn.model_selection import train_test_split
import yaml
import os

def main():
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)

    df = pd.read_excel('data/cleaned_data.xlsx')

    grade_matrix = df.pivot_table(index='admi', columns='code', values='note', aggfunc='first')

    courses_s1_s4 = []
    courses_s5_s6 = []

    for sem in ['S1', 'S2', 'S3', 'S4']:
        courses_s1_s4.extend(df[df['simester'] == sem]['code'].unique().tolist())
    for sem in ['S5', 'S6']:
        courses_s5_s6.extend(df[df['simester'] == sem]['code'].unique().tolist())

    courses_s1_s4 = list(dict.fromkeys([c for c in courses_s1_s4 if c in grade_matrix.columns]))
    courses_s5_s6 = list(dict.fromkeys([c for c in courses_s5_s6 if c in grade_matrix.columns]))

    X = grade_matrix[courses_s1_s4].fillna(grade_matrix[courses_s1_s4].median())
    y = grade_matrix[courses_s5_s6].fillna(grade_matrix[courses_s5_s6].median())

    data = pd.concat([X, y], axis=1)
    data = data.reset_index()

    train_data, test_data = train_test_split(
        data,
        test_size=params['train']['test_size'],
        random_state=params['train']['random_state']
    )

    os.makedirs('data/processed', exist_ok=True)
    train_data.to_csv('data/processed/train.csv', index=False)
    test_data.to_csv('data/processed/test.csv', index=False)

    print(f"Train size: {len(train_data)}, Test size: {len(test_data)}")
    print(f"Input courses: {len(courses_s1_s4)}, Output courses: {len(courses_s5_s6)}")

if __name__ == '__main__':
    main()