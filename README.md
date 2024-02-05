# Japanese Kanji Quiz

Minimalist Japanese Hiragana/Katakana/Kanji Quiz. 

----

This python-based quiz was written to quickly memorize Hiragana/Katakana/Kanji. You can get this by downloading Anaconda3. Make sure you have the required python packages installed by running: 

```
pip install -r requirements.txt
```

Basic Features: 

Add your own quizzes to the vocab folder to have them automatically added to the program. Hiragana and Katana quizzes are already placed in the alphabets folder. Words that are missed in non-alphabet quizzes will be stored in `missed/missed-words.csv`. You can clear the words in these files by clicking the "Clear Missed Words" button. If you add new words while the program is open you can click the "Reload Quizzes" button to refresh the program. I like to add all work to a single file in all-words to quiz while I am watching TV so feel free to add any words to that in your own file. Remaining words and the percentage of words correct while quizzing will display on the bottom.

The all-words quiz will remove a word from the quiz if $t_l + n\times2^m < t_c$, where $t_l$ is the last time you got the word right, $n$ is the interval time (default to two weeks), $m$ is the number of times you have got the word correct in a row, and $t_c$ is the current time. You can change the interval time to be shorter or longer by changing:

```
self.interval_time = 604800 * 2 # 2 weeks in seconds
```

in 'japanese-quiz.py'. Words are only added to the counter if you get them correct in the all-words quiz. You can view which words you have gotten correct and how many times in a row you have gotten them correct in the `counter.csv`.

If you want to use the .bat script to launch the gui you will need to either replace or remove the environment call.

Enjoy!

Sample Quizzes
![](/readme-images/quizzes.png)

Correct Words
![](/readme-images/correct.png)

Incorrect Words
![](/readme-images/incorrect.png)