# Dataset descriptives

2034 companies, YC batches 2005–2019, 75 model features

## Status

| status   |   n |   share |
|:---------|----:|--------:|
| Active   | 820 |   0.403 |
| Acquired | 535 |   0.263 |
| Inactive | 657 |   0.323 |
| Public   |  22 |   0.011 |

## Categorical features

|             |   levels | most common                     | share   |
|:------------|---------:|:--------------------------------|:--------|
| industry    |        9 | B2B                             | 40%     |
| subindustry |       59 | Engineering, Product and Design | 8%      |
| country     |       58 | United States of America        | 79%     |
| city        |      196 | San Francisco                   | 51%     |

## Numeric / binary features

|                                     | group      |     mean |    std |   min |      50% |     max |
|:------------------------------------|:-----------|---------:|-------:|------:|---------:|--------:|
| batch_year                          | A launch   | 2015.21  |  3.329 |  2005 | 2016     | 2019    |
| is_winter_batch                     | A launch   |    0.494 |  0.5   |     0 |    0     |    1    |
| is_usa                              | A launch   |    0.791 |  0.407 |     0 |    1     |    1    |
| region_america_canada               | A launch   |    0.834 |  0.372 |     0 |    1     |    1    |
| region_europe                       | A launch   |    0.059 |  0.237 |     0 |    0     |    1    |
| region_south_asia                   | A launch   |    0.028 |  0.165 |     0 |    0     |    1    |
| region_latin_america                | A launch   |    0.023 |  0.15  |     0 |    0     |    1    |
| region_southeast_asia               | A launch   |    0.012 |  0.108 |     0 |    0     |    1    |
| region_africa                       | A launch   |    0.012 |  0.108 |     0 |    0     |    1    |
| region_middle_east_and_north_africa | A launch   |    0.011 |  0.106 |     0 |    0     |    1    |
| region_east_asia                    | A launch   |    0.008 |  0.091 |     0 |    0     |    1    |
| is_bay_area                         | A launch   |    0.511 |  0.5   |     0 |    1     |    1    |
| is_nyc                              | A launch   |    0.094 |  0.292 |     0 |    0     |    1    |
| n_locations                         | A launch   |    1.446 |  0.722 |     0 |    1     |   12    |
| tags_count                          | A launch   |    2.025 |  1.249 |     0 |    2     |    6    |
| n_industries                        | A launch   |    1.909 |  0.288 |     1 |    2     |    2    |
| tag_saas                            | A launch   |    0.129 |  0.336 |     0 |    0     |    1    |
| tag_fintech                         | A launch   |    0.094 |  0.292 |     0 |    0     |    1    |
| tag_ai                              | A launch   |    0.092 |  0.289 |     0 |    0     |    1    |
| tag_marketplace                     | A launch   |    0.075 |  0.263 |     0 |    0     |    1    |
| tag_b2b                             | A launch   |    0.075 |  0.263 |     0 |    0     |    1    |
| tag_e_commerce                      | A launch   |    0.049 |  0.216 |     0 |    0     |    1    |
| tag_developer_tools                 | A launch   |    0.048 |  0.214 |     0 |    0     |    1    |
| tag_education                       | A launch   |    0.038 |  0.191 |     0 |    0     |    1    |
| tag_hardware                        | A launch   |    0.031 |  0.175 |     0 |    0     |    1    |
| tag_analytics                       | A launch   |    0.03  |  0.172 |     0 |    0     |    1    |
| tag_machine_learning                | A launch   |    0.03  |  0.171 |     0 |    0     |    1    |
| tag_health_tech                     | A launch   |    0.029 |  0.168 |     0 |    0     |    1    |
| tag_healthcare                      | A launch   |    0.027 |  0.161 |     0 |    0     |    1    |
| tag_logistics                       | A launch   |    0.023 |  0.15  |     0 |    0     |    1    |
| tag_payments                        | A launch   |    0.023 |  0.149 |     0 |    0     |    1    |
| tag_climate                         | A launch   |    0.023 |  0.149 |     0 |    0     |    1    |
| tag_consumer                        | A launch   |    0.022 |  0.147 |     0 |    0     |    1    |
| tag_gaming                          | A launch   |    0.021 |  0.144 |     0 |    0     |    1    |
| tag_social                          | A launch   |    0.02  |  0.141 |     0 |    0     |    1    |
| tag_biotech                         | A launch   |    0.02  |  0.141 |     0 |    0     |    1    |
| tag_productivity                    | A launch   |    0.019 |  0.137 |     0 |    0     |    1    |
| tag_video                           | A launch   |    0.019 |  0.137 |     0 |    0     |    1    |
| tag_iot                             | A launch   |    0.017 |  0.128 |     0 |    0     |    1    |
| tag_real_estate                     | A launch   |    0.016 |  0.126 |     0 |    0     |    1    |
| tag_api                             | A launch   |    0.016 |  0.124 |     0 |    0     |    1    |
| tag_marketing                       | A launch   |    0.016 |  0.124 |     0 |    0     |    1    |
| tag_consumer_health_services        | A launch   |    0.016 |  0.124 |     0 |    0     |    1    |
| tag_recruiting                      | A launch   |    0.015 |  0.123 |     0 |    0     |    1    |
| tag_messaging                       | A launch   |    0.015 |  0.123 |     0 |    0     |    1    |
| tag_digital_health                  | A launch   |    0.015 |  0.123 |     0 |    0     |    1    |
| is_nonprofit                        | A launch   |    0.018 |  0.132 |     0 |    0     |    1    |
| has_demo_day_video                  | A launch   |    0.04  |  0.197 |     0 |    0     |    1    |
| has_app_video                       | A launch   |    0.012 |  0.108 |     0 |    0     |    1    |
| has_question_answers                | A launch   |    0.022 |  0.147 |     0 |    0     |    1    |
| name_length                         | A launch   |    9.008 |  4.429 |     2 |    8     |   44    |
| name_words                          | A launch   |    1.288 |  0.611 |     1 |    1     |    7    |
| name_has_digit                      | A launch   |    0.017 |  0.128 |     0 |    0     |    1    |
| has_website                         | B presence |    0.898 |  0.303 |     0 |    1     |    1    |
| tld_com                             | B presence |    0.714 |  0.452 |     0 |    1     |    1    |
| tld_io                              | B presence |    0.043 |  0.202 |     0 |    0     |    1    |
| tld_co                              | B presence |    0.027 |  0.161 |     0 |    0     |    1    |
| tld_ai                              | B presence |    0.03  |  0.171 |     0 |    0     |    1    |
| tld_org                             | B presence |    0.018 |  0.132 |     0 |    0     |    1    |
| has_logo                            | B presence |    0.698 |  0.459 |     0 |    1     |    1    |
| has_location                        | B presence |    0.967 |  0.179 |     0 |    1     |    1    |
| n_former_names                      | B presence |    0.67  |  1.13  |     0 |    0     |   13    |
| one_liner_len                       | B presence |   47.389 | 20.248 |     0 |   53     |   70    |
| description_len_log                 | B presence |    5.422 |  1.873 |     0 |    5.941 |    8.97 |
| description_words                   | B presence |   71.073 | 63.342 |     0 |   58     | 1121    |
| has_description                     | B presence |    0.91  |  0.287 |     0 |    1     |    1    |
| has_partner                         | B presence |    0.06  |  0.238 |     0 |    0     |    1    |
| team_size_log                       | C current  |    2.723 |  1.713 |     0 |    2.485 |    9.21 |
| is_hiring                           | C current  |    0.127 |  0.333 |     0 |    0     |    1    |
| is_top_company                      | C current  |    0.043 |  0.202 |     0 |    0     |    1    |
| stage_growth                        | C current  |    0.341 |  0.474 |     0 |    0     |    1    |
| is_remote                           | C current  |    0.495 |  0.5   |     0 |    0     |    1    |
