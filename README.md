# tbr-anticipated-releases

This project scrapes a user's goodreads to-read list using python and outputs:

1. A list of books coming out in the next week
2. A list of books released in the past month

Currently goodreads doesn't notify users when books on their to-read list have been published. To solve this problem this project was created to provide the user with an easily accessible list of recently published books from their goodreads profile.

`main.py` scrapes goodreads and output 3 data files:
1. `full_tbr` which contains data on all books on the to-read list
2. `tbr_past_month` which contains data on books released in the past month
3. `tbr_coming_week` which contains data on books which will be released in the upcoming week.

`index.html` then displays that data on a web page.
