# ResMeth Reliability

A Python-based reliability coefficient for quantitative studies. The app automates the calculation of multiple internal consistency coefficients and inter-rater agreement coefficients.

## How to Use

1. Convert your data into comma-delimiter CSV file. Ensure your data is in comma-delimiter CSV.
2. Upload your data
3. Preview your data
4. Assign your data based on the parameters
  * If you use Internal Consistency, the app should automatically calculate all available coefficients
  * If you use Inter-rater Agreement, you need to manually set the number of raters and type of data
5. Run analysis

## Data Structure

Data accepted in this web app follow the following rules:

| Header |
|-|
| Data |
| Data |
| Data |

**NOTE**: The first line of your data expects **header**, it will not be counted as data.

The following is the example of comma-delimiter CSV.

```
R1,R2,R3,R4,R5,R6
63,70,66,66,66,62
62,69,71,62,64,70
63,74,70,75,60,74
58,76,80,75,72,76
59,65,63,60,66,76
62,80,76,76,76,90
76,69,71,74,72,86
67,81,77,65,64,86
72,62,66,71,72,72
60,58,62,76,62,62
59,71,75,74,74,74
64,79,75,76,76,76
66,64,60,72,72,72
60,80,76,70,70,70
68,70,74,65,65,65
85,69,65,74,74,74
```

## Example of Data: Format 1

The example above should look like the following on the web app.

| R1 | R2 | R3 | R4 | R5 | R6 |
|-|-|-|-|-|-|
| 63 | 70 | 66 | 66 | 66 | 62 |
| 62 | 69 | 71 | 62 | 64 | 70 |
| 63 | 74 | 70 | 75 | 60 | 74 |
| 58 | 76 | 80 | 75 | 72 | 76 |
| 59 | 65 | 63 | 60 | 66 | 76 |
| 62 | 80 | 76 | 76 | 76 | 90 |
| 76 | 69 | 71 | 74 | 72 | 86 |
| 67 | 81 | 77 | 65 | 64 | 86 |
| 72 | 62 | 66 | 71 | 72 | 72 |
| 60 | 58 | 62 | 76 | 62 | 62 |
| 59 | 71 | 75 | 74 | 74 | 74 |
| 64 | 79 | 75 | 76 | 76 | 76 |
| 66 | 64 | 60 | 72 | 72 | 72 |
| 60 | 80 | 76 | 70 | 70 | 70 |
| 68 | 70 | 74 | 65 | 65 | 65 |
| 85 | 69 | 65 | 74 | 74 | 74 |

## Example of Data: Format 2

Your data can also appear in the following format:

| No. | R1 | R2 | R3 | R4 | R5 | R6 |
|-|-|-|-|-|-|-|
| 1. | 63 | 70 | 66 | 66 | 66 | 62 |
| 2.| 62 | 69 | 71 | 62 | 64 | 70 |
| 3.| 63 | 74 | 70 | 75 | 60 | 74 |
| 4.| 58 | 76 | 80 | 75 | 72 | 76 |
| 5.| 59 | 65 | 63 | 60 | 66 | 76 |
| 6.| 62 | 80 | 76 | 76 | 76 | 90 |
| 7.| 76 | 69 | 71 | 74 | 72 | 86 |
| 8.| 67 | 81 | 77 | 65 | 64 | 86 |
| 9.| 72 | 62 | 66 | 71 | 72 | 72 |
| 10.| 60 | 58 | 62 | 76 | 62 | 62 |
| 11.| 59 | 71 | 75 | 74 | 74 | 74 |
| 12.| 64 | 79 | 75 | 76 | 76 | 76 |
| 13.| 66 | 64 | 60 | 72 | 72 | 72 |
| 14.| 60 | 80 | 76 | 70 | 70 | 70 |
| 15.| 68 | 70 | 74 | 65 | 65 | 65 |
| 16.| 85 | 69 | 65 | 74 | 74 | 74 |

## Example of Data: Format 3

Your data can also appear in the following format:

| No. | Name | R1 | R2 | R3 | R4 | R5 | R6 |
|-|-|-|-|-|-|-|-|
| 1. | Aria | 63 | 70 | 66 | 66 | 66 | 62 |
| 2.| Kai | 62 | 69 | 71 | 62 | 64 | 70 |
| 3.| Luna | 63 | 74 | 70 | 75 | 60 | 74 |
| 4.| John | 58 | 76 | 80 | 75 | 72 | 76 |
| 5.| Eden | 59 | 65 | 63 | 60 | 66 | 76 |
| 6.| Emma | 62 | 80 | 76 | 76 | 76 | 90 |
| 7.| Noah | 76 | 69 | 71 | 74 | 72 | 86 |
| 8.| Sam | 67 | 81 | 77 | 65 | 64 | 86 |

## About Us

**ResMeth Reliability** is developed by **Muhaimin Abdullah**, **Ahmad Munir**, **Wiwiet Eva Savitri**, and **Widya Rizky Pratiwi**. This app is intended to help professional researchers, lecturers, and students in dealing with internal consistency and inter-rater agreement. 
