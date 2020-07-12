'''
command line program to analyze bikeshare data
'''
import logging
import time
import pandas as pd
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.WARNING)


CITY_DATA = {'chicago': 'chicago.csv',
             'new york city': 'new_york_city.csv',
             'washington': 'washington.csv'}


def read_limited_string(available_options,
                        pre_options_mesg='select one of the following options:\n',):
    ''' read a string that can only match a list of options

    Args:
        available_options (list): list of string to choose from
        pre_options_mesg (string): message for user before options

    Returns:
        selected_option (str): the selected item from list of options
                                or string(all) representing all items

    Throws:
        ValueError : if available_options is empty list
    '''

    if len(available_options) == 0:
        raise ValueError("available_options cannot be null")

    # prepare message for user input
    input_message = pre_options_mesg + '\n'

    # add all as option without editing original list
    options = available_options.copy() + ['all']

    # add available_options to input message
    for i, option in enumerate(options, start=1):
        input_message += '{option_num}) {option}\t\t'.format(
            option_num=i, option=option)

    # try reading option from user
    while True:
        option = input(input_message+'\n\n your choice (number or string)>')
        print('\n')

        # if input is number change it to string
        try:
            option = int(option)
            # -1 because enumerate start at 1
            option = options[option-1]

        # the input is string
        except ValueError:
            pass

        # the input is number out boundaries
        except IndexError:
            pass

        if option in options:
            break  # break while loop we get our option

        # else ask for value again
        print("{option} is not found in options make sure to use available option\n\n".format(
            option=option))

    return option


def select_from_multible(available_options, input_message):
    """
    Asks user to specify a option/options

    Args:
        available_options (list): list of string to choose from
        pre_options_mesg (string): message for user before selecting only prented once


    Returns:
        selected (list): list of selected options
    """

    add_more = True

    # copy of the list that removes selected options
    remaining_options = available_options.copy()
    selected_options = []
    while add_more:
        # add available_options to input message
        option = read_limited_string(remaining_options, input_message)

        if option == 'all':
            return available_options

        # remove selected option to prevent duplicate loading
        remaining_options.remove(option)

        selected_options.append(option)

        # make sure there is other options
        if len(remaining_options) > 0:
            # check if user wanna load more options
            add_more = yes_no("select more options (y/n):")
        else:
            add_more = False

        # update input message
        input_message = '{} is/are selected'.format(selected_options)

    return selected_options


def yes_no(question):
    ''' force retrive answer for yes or no question

    Args:
    (str) question

    returns:
    (boolean) response '''

    yes = ['y', 'yes']
    no = ['n', 'no']

    while True:
        choice = input(question)
        if choice in yes:
            response = True
            break

        if choice in no:
            response = False
            break

        # ask again untill choice is (y or n)
        print("please select yes or no \n")

    return response


def load_data():
    '''
    Asks user to specify a city, month, and day to analyze.

    Returns:
        df (pandas.DataFrame) : loaded data as pandas.DataFrame
    '''

    print('Hello! Let\'s explore some US bikeshare data!')

    available_cities = list(CITY_DATA.keys())

    # prepare message for user input
    input_message = 'select city to explore'

    cities = select_from_multible(available_cities, input_message)
    df = pd.DataFrame()
    for city in cities:
        df = load_city_data(city, df)
        print('{} loaded successfully\n'.format(city))
        if logging.root.level == logging.DEBUG:
            df.info()

    # add month and day_of_week column
    df = prepare_time_data(df)

    # get available months for user to select
    available_months = list(df['month'].unique())

    if yes_no("do you want to apply a time filter ?"):
        # promote user to select month/months
        select_month_message = 'select month to keep'
        months = select_from_multible(available_months, select_month_message)

        # if user selected all don't apply fillter
        keep_all_months = sorted(available_months) == sorted(
            months) and len(months) > 0

        # get available days for user to select
        available_days = list(df['day_of_week'].unique())

        # promote user to select day/days
        select_day_message = 'select day to keep'
        days = select_from_multible(available_days, select_day_message)

        # if user selected all don't apply fillter
        keep_all_days = sorted(available_days) == sorted(
            days) and len(days) > 0

        # apply month and day fillter
        df = apply_time_filters(
            df, months, days, keep_all_months, keep_all_days)
        if logging.root.level == logging.DEBUG:
            df.info()

        print("filter applied successfully")
        print('-'*40)

    return df


def load_city_data(city, df=None):
    ''' load dataframe for selected city

    Args:
        city (str): city name as string
        df (pandas.DataFrame) default None: dataframe previosly loaded to append
        or none to create new

    returns:
        data : related city data as pandas.DataFrame
    '''
    if df is None:
        # load data file into a dataframe
        return pd.read_csv(CITY_DATA[city])

    # append the dataframe if not None
    return df.append(pd.read_csv(CITY_DATA[city]))


def prepare_time_data(df):
    ''' add month and day_of_week to dataframe'''

    # convert the Start Time column to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])

    # extract month and day of week from Start Time to create new columns
    df['month'] = df['Start Time'].dt.month_name()
    df['day_of_week'] = df['Start Time'].dt.day_name()
    df['start_hour'] = df['Start Time'].dt.hour

    return df


def apply_time_filters(df, months, days, keep_all_months=False, keep_all_days=False):
    """
    keep the data specified by months and days filteres

    Args:
        (list) month - name of the months to keep in data
        (str) day - name of the days of week to keep in data

    Returns:
        df - Pandas DataFrame filtered by month and day
    """
    # filter by month if keep all is false
    if not keep_all_months:
        df = df.loc[df['month'].isin(months)]
    # filter by day of week if keep all is false
    if not keep_all_days:
        df = df.loc[df['day_of_week'].isin(days)]

    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    # display the most common month
    months_freq = df['month'].value_counts()
    print("most common month is --> {} by {} trips\n".format(
        months_freq.index[0], months_freq.iloc[0]
    ))

    # display the most common day of week
    day_freq = df['day_of_week'].value_counts()
    print("most common day is --> {} by {} trips\n".format(
        day_freq.index[0], day_freq.iloc[0]
    ))

    # display the most common start hour
    hour_freq = df['start_hour'].value_counts()
    logging.debug(hour_freq)
    print("most common start hour is --> {} by {} trips\n".format(
        hour_freq.index[0], hour_freq.iloc[0]
    ))

    logging.debug(months_freq)
    logging.debug(day_freq)
    logging.debug(hour_freq)

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # display most commonly used start station
    start_freq = df['Start Station'].value_counts()
    print("most common start station is :\n{} by {} trips\n".format(
        start_freq.index[0], start_freq.iloc[0]
    ))

    # display most commonly used end station
    end_freq = df['End Station'].value_counts()
    print("most common end station is :\n{} by {} trips\n".format(
        end_freq.index[0], end_freq.iloc[0]
    ))
    # display most frequent combination of start station and end station trip
    # combine start and end to count them
    start_end_freq = (df['Start Station']+' --> ' +
                      df['End Station']).value_counts()

    combination_start, combination_end = start_end_freq.index[0].split('-->')

    print("most common combination is :\n" +
          "start =>  {}\nend  => {}\ntrips => {}".format(
              combination_start, combination_end, start_end_freq.iloc[0]
          ))

    logging.debug(start_freq)
    logging.debug(end_freq)
    logging.debug(start_end_freq)

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def human_time(time_seconds):
    '''print seconds in human readable format
    source https://www.w3resource.com/python-exercises/python-basic-exercise-65.php'''
    remaining_time = time_seconds

    day = remaining_time // (24 * 3600)
    remaining_time = remaining_time % (24 * 3600)

    hour = remaining_time // 3600
    remaining_time %= 3600

    minutes = remaining_time // 60
    remaining_time %= 60
    seconds = remaining_time
    print("d:h:m:s-> {}:{}:{}:{}".format(day, hour, minutes, seconds))


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # display total travel time
    total_time = df['Trip Duration'].sum()
    print("total trip duration is ")
    human_time(total_time)
    print('in seconds =  {} s'.format(total_time))

    # display mean travel time
    mean_time = round(df['Trip Duration'].mean())
    print("\naverage trip duration is ")
    human_time(mean_time)
    print('mean {} s'.format(mean_time))

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # Display counts of user types
    user_type_freq = df['User Type'].value_counts()
    print("\ntype of users : ")
    print(user_type_freq.to_string())
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

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)


def main():
    ''' start the program '''
    while True:
        df = load_data()

        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        count = 0
        batch = 5
        while True:
            if yes_no("see row data ?"):
                try:
                    print(df[count:count+batch].to_json())
                except KeyError:
                    print("no more data available")
            else:
                break
            count += batch
        restart = yes_no("\nWould you like to restart?")
        if not restart:
            break


if __name__ == "__main__":
    main()
