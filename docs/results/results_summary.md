# Baseline results

## Cross-validation (5-fold stratified, repeated 3x)

| task     | features   | model               |    n |   pos_rate |   roc_auc |   pr_auc |   bal_acc |    f1 |   roc_auc_std |
|:---------|:-----------|:--------------------|-----:|-----------:|----------:|---------:|----------:|------:|--------------:|
| exit     | A          | Dummy (majority)    | 1214 |      0.459 |     0.5   |    0.459 |     0.5   | 0     |         0     |
| exit     | A          | Logistic Regression | 1214 |      0.459 |     0.645 |    0.605 |     0.611 | 0.581 |         0.03  |
| exit     | A          | Random Forest       | 1214 |      0.459 |     0.66  |    0.61  |     0.613 | 0.588 |         0.025 |
| exit     | A          | Gradient Boosting   | 1214 |      0.459 |     0.641 |    0.59  |     0.603 | 0.576 |         0.023 |
| exit     | A+B        | Logistic Regression | 1214 |      0.459 |     0.72  |    0.688 |     0.67  | 0.646 |         0.032 |
| exit     | A+B        | Random Forest       | 1214 |      0.459 |     0.731 |    0.695 |     0.67  | 0.647 |         0.018 |
| exit     | A+B        | Gradient Boosting   | 1214 |      0.459 |     0.718 |    0.678 |     0.66  | 0.634 |         0.018 |
| exit     | A+B+C      | Logistic Regression | 1214 |      0.459 |     0.773 |    0.775 |     0.71  | 0.68  |         0.03  |
| exit     | A+B+C      | Random Forest       | 1214 |      0.459 |     0.785 |    0.786 |     0.707 | 0.673 |         0.019 |
| exit     | A+B+C      | Gradient Boosting   | 1214 |      0.459 |     0.778 |    0.777 |     0.715 | 0.683 |         0.023 |
| exit     | text (B)   | TF-IDF + LogReg     | 1214 |      0.459 |     0.658 |    0.623 |     0.62  | 0.591 |         0.025 |
| survival | A          | Dummy (majority)    | 2034 |      0.677 |     0.5   |    0.677 |     0.5   | 0.807 |         0     |
| survival | A          | Logistic Regression | 2034 |      0.677 |     0.706 |    0.829 |     0.651 | 0.705 |         0.022 |
| survival | A          | Random Forest       | 2034 |      0.677 |     0.719 |    0.832 |     0.654 | 0.731 |         0.025 |
| survival | A          | Gradient Boosting   | 2034 |      0.677 |     0.72  |    0.839 |     0.661 | 0.717 |         0.025 |
| survival | A+B        | Logistic Regression | 2034 |      0.677 |     0.792 |    0.884 |     0.726 | 0.789 |         0.018 |
| survival | A+B        | Random Forest       | 2034 |      0.677 |     0.807 |    0.891 |     0.746 | 0.812 |         0.021 |
| survival | A+B        | Gradient Boosting   | 2034 |      0.677 |     0.804 |    0.891 |     0.735 | 0.804 |         0.019 |
| survival | A+B+C      | Logistic Regression | 2034 |      0.677 |     0.846 |    0.925 |     0.767 | 0.805 |         0.014 |
| survival | A+B+C      | Random Forest       | 2034 |      0.677 |     0.859 |    0.929 |     0.779 | 0.822 |         0.015 |
| survival | A+B+C      | Gradient Boosting   | 2034 |      0.677 |     0.857 |    0.929 |     0.779 | 0.826 |         0.015 |
| survival | text (B)   | TF-IDF + LogReg     | 2034 |      0.677 |     0.691 |    0.82  |     0.637 | 0.742 |         0.022 |

## Temporal hold-out (train <= 2015, test 2016-2019)

| task     | features   | model               |   n_train |   n_test |   roc_auc |   pr_auc |   bal_acc |    f1 |
|:---------|:-----------|:--------------------|----------:|---------:|----------:|---------:|----------:|------:|
| exit     | A          | Dummy (majority)    |       683 |      531 |     0.5   |    0.424 |     0.5   | 0     |
| exit     | A          | Logistic Regression |       683 |      531 |     0.617 |    0.533 |     0.585 | 0.524 |
| exit     | A          | Random Forest       |       683 |      531 |     0.651 |    0.564 |     0.626 | 0.622 |
| exit     | A          | Gradient Boosting   |       683 |      531 |     0.642 |    0.563 |     0.592 | 0.579 |
| exit     | A+B        | Dummy (majority)    |       683 |      531 |     0.5   |    0.424 |     0.5   | 0     |
| exit     | A+B        | Logistic Regression |       683 |      531 |     0.644 |    0.543 |     0.608 | 0.564 |
| exit     | A+B        | Random Forest       |       683 |      531 |     0.699 |    0.598 |     0.616 | 0.622 |
| exit     | A+B        | Gradient Boosting   |       683 |      531 |     0.68  |    0.567 |     0.645 | 0.619 |
| survival | A          | Dummy (majority)    |       924 |     1110 |     0.5   |    0.724 |     0.5   | 0.84  |
| survival | A          | Logistic Regression |       924 |     1110 |     0.662 |    0.834 |     0.62  | 0.746 |
| survival | A          | Random Forest       |       924 |     1110 |     0.688 |    0.836 |     0.635 | 0.823 |
| survival | A          | Gradient Boosting   |       924 |     1110 |     0.684 |    0.838 |     0.619 | 0.805 |
| survival | A+B        | Dummy (majority)    |       924 |     1110 |     0.5   |    0.724 |     0.5   | 0.84  |
| survival | A+B        | Logistic Regression |       924 |     1110 |     0.727 |    0.863 |     0.641 | 0.796 |
| survival | A+B        | Random Forest       |       924 |     1110 |     0.763 |    0.875 |     0.66  | 0.856 |
| survival | A+B        | Gradient Boosting   |       924 |     1110 |     0.74  |    0.864 |     0.658 | 0.835 |

## Top 15 features – RF permutation importance (exit, A+B)

| feature             |   importance |    std |
|:--------------------|-------------:|-------:|
| has_logo            |       0.0716 | 0.022  |
| industry            |       0.0144 | 0.0061 |
| batch_year          |       0.0125 | 0.0056 |
| tld_com             |       0.0096 | 0.0041 |
| has_website         |       0.0093 | 0.0046 |
| name_length         |       0.0082 | 0.0032 |
| tag_saas            |       0.0075 | 0.0049 |
| subindustry         |       0.0066 | 0.0038 |
| n_locations         |       0.0037 | 0.0033 |
| description_len_log |       0.0034 | 0.0087 |
| tag_fintech         |       0.0033 | 0.0017 |
| tag_analytics       |       0.0027 | 0.0011 |
| country             |       0.0018 | 0.0023 |
| has_partner         |       0.0017 | 0.0007 |
| has_location        |       0.0016 | 0.0014 |
