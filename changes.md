# washinton has missing data
```
The query provides an error when we select washington. Please note that the dataset for washington has no fields for gender and Birth year. Use a conditional statement when calculating the user_statistics to exclude this city.
```

i have already handeled this case by this try ,except 
```python
    try:
        # Display counts of gender
        user_gender_freq = df['Gender'].value_counts()
        print("\ngender of users : ")
        print(user_gender_freq.to_string())

        # Display earliest, most recent, and most common year of birth
        user_earliest_birth = df['Birth Year'].min()
        user_recent_birth = df['Birth Year'].max()
        user_common_birth = round(df['Birth Year'].mode())[0]

        print("\nbirth of users : ")
        print('user_earliest_birth --> {}\n'.format(user_earliest_birth))
        print('user_recent_birth --> {}\n'.format(user_recent_birth))
        print('user_common_birth --> {}\n'.format(user_common_birth))

    except KeyError:
        print("gender & birth data is not available")
```

the problem was here when trying to get time trend when applying lots of fillters
hour zero will get no value so will throw KeyValue error

```python
   print("most common start hour is --> {} by {} trips\n".format(
        hour_freq.index[0], hour_freq[0]
    ))
```

thanks for your tip i am using `iloc()` and no error is thrown and 
number of trips is now correct
```python
print("most common start hour is --> {} by {} trips\n".format(
        hour_freq.index[0], hour_freq.iloc[0]
    ))
```