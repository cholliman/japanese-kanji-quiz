import numpy as _np
import pandas as _pd
import os
import csv
import time
from sklearn.utils import shuffle
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import QFont


class Quiz(QtWidgets.QWidget):
    '''
    Japanese Quiz
    Craig Holliman
    '''

    def __init__(self, reactor):
        super().__init__()

        self.empty_file_1 = False
        self._define_directories()
        self._load_vocab(self.alphabet_directory, self.alphabet, self.alphabet_name)
        self._load_vocab(self.missed_directory, self.missed, self.missed_name)
        self._load_vocab(self.vocab_directory, self.vocab, self.vocab_name)
        self._load_vocab(self.all_words_directory, self.all_words, self.all_words_name)

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.reactor = reactor
        self.current_time = time.time()
        self.interval_time = 604800 * 2 # 2 weeks in seconds
        self.initUI()

    def _define_directories(self):
        self.alphabet_directory = "alphabets/"
        self.alphabet = []
        self.alphabet_name = []

        # add your own quizzes here
        self.vocab_directory = "vocab/"
        self.vocab = []
        self.vocab_name = []

        self.missed_directory = "missed/"
        self.missed = []
        self.missed_name = []

        self.all_words_directory = "all-words/"
        self.all_words = []
        self.all_words_name = []

        self.missed_words = "missed/missed-words.csv"

        self.df_counter = _pd.read_csv('counters/counter.csv')
        self.counter_kanji = _np.array(self.df_counter['kanji'])
        self.counter_counter = _np.array(self.df_counter['counter'])
        self.counter_time = _np.array(self.df_counter['time'])

    def _load_vocab(self, directory, contents, quiz_name):
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                name = filename.split('.')[0]
                quiz_name.append(name)
                try:
                    lesson = _pd.read_csv(str(directory + filename), skiprows=1, header=None)
                    contents.append(lesson)
                except _pd.errors.EmptyDataError:
                    if name == 'missed-words':
                        self.empty_file_1 = True
                    pass
                continue
            else:
                for file in os.listdir(directory + str(filename) + '/'):
                    name = file.split('.')[0]
                    quiz_name.append(name)
                    lesson =  _pd.read_csv(str(directory + str(filename) + '/' + file),
                                           skiprows=1, header=None)
                    contents.append(lesson)
                    continue

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        layout = QtWidgets.QGridLayout()
        qBox = QtWidgets.QGroupBox("Japanese Quiz")
        qBox.setFont(QFont('Times', 20))

        subLayout = QtWidgets.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)
        QtWidgets.QToolTip.setFont(QFont('Times', 18))

        # select text
        self.select_text = QtWidgets.QLabel(self)
        self.select_text.setFont(QFont('Times', 16))
        self.select_text.setText('Select Quiz')
        self.select_text.setAlignment(QtCore.Qt.AlignLeft)    

        # select menu
        self.select = QtWidgets.QComboBox(self)
        self.select.addItem('all-words-newest-25')
        for i in self.all_words_name:
            self.select.addItem(i)
        for i in self.alphabet_name:
            self.select.addItem(i)
        for i in self.missed_name:
            self.select.addItem(i)
        for i in self.vocab_name:
            self.select.addItem(i)
        self.select.setFont(QFont('Times', 14))
        self.select.activated[str].connect(self.selectActivated)

        # character display
        self.character_btn = QtWidgets.QPushButton('', self)
        self.character_btn.setFont(QFont('Times', 60))

        # character entry label
        self.character_entry_label = QtWidgets.QLabel(self)
        self.character_entry_label.setFont(QFont('Times', 14))
        self.character_entry_label.setText('ローマ字 (Romaji)')
        self.character_entry_label.setAlignment(QtCore.Qt.AlignCenter)

        # romaji entry
        self.character_entry = QtWidgets.QLineEdit(self)
        self.character_entry.returnPressed.connect(self.storeValue)
        self.character_entry.setFont(QFont('Times', 30))

        # meaning entry label
        self.meaning_entry_label = QtWidgets.QLabel(self)
        self.meaning_entry_label.setFont(QFont('Times', 14))
        self.meaning_entry_label.setText('意味 (Meaning)')
        self.meaning_entry_label.setAlignment(QtCore.Qt.AlignCenter)

        # meaning entry
        self.meaning_entry = QtWidgets.QLineEdit(self)
        self.meaning_entry.returnPressed.connect(self.storeValue)
        self.meaning_entry.setFont(QFont('Times', 30))
        
        # remaining characters
        self.num_of_characters = QtWidgets.QLabel(self)
        self.num_of_characters.setFont(QFont('Times', 14))
        self.num_of_characters.setText('Characters Remaining: ')

        # previous header
        self.prev_head = QtWidgets.QLabel(self)
        self.prev_head.setFont(QFont('Times', 16))
        self.prev_head.setText('The Previous Word')
        self.prev_head.setAlignment(QtCore.Qt.AlignCenter)

        # previous kanji
        self.prev_kanji = QtWidgets.QLabel(self)
        self.prev_kanji.setFont(QFont('Times', 32))
        self.prev_kanji.setAlignment(QtCore.Qt.AlignCenter)
        
        # previous meaning
        self.prev_meaning = QtWidgets.QLabel(self)
        self.prev_meaning.setFont(QFont('Times', 16))
        self.prev_meaning.setAlignment(QtCore.Qt.AlignLeft)

        # question status, correct/incorrect/quiz done
        self.question_status = QtWidgets.QLabel(self)
        self.question_status.setFont(QFont('Times', 22))
        self.question_status.setAlignment(QtCore.Qt.AlignLeft)

        # percent correct
        self.percent_correct = QtWidgets.QLabel(self)
        self.percent_correct.setFont(QFont('Times', 14))
        self.percent_correct.setText('Percent Correct: ')

        # clear button
        self.clear_btn = QtWidgets.QPushButton('Clear Missed Words', self)
        self.clear_btn.setFont(QFont('Times', 12))
        self.clear_btn.clicked.connect(self.clear_button)

        # reload button
        self.reload_btn = QtWidgets.QPushButton('Reload Quizes', self)
        self.reload_btn.setFont(QFont('Times', 12))
        self.reload_btn.clicked.connect(self.reload_button)

        # (row, column, rowspan, columnspan)
        subLayout.addWidget(self.select_text, 0, 0, 1, 2) # select text
        subLayout.addWidget(self.select, 1, 0, 1, 2) # select menu
        subLayout.addWidget(self.clear_btn, 2, 0, 1, 1) # clear button
        subLayout.addWidget(self.reload_btn, 2, 1, 1, 1) # reload button

        subLayout.addWidget(self.prev_head, 0, 2, 1, 4) # previous header
        subLayout.addWidget(self.prev_kanji, 1, 2, 2, 2) # previous kanji
        subLayout.addWidget(self.prev_meaning, 1, 4, 2, 2) # previous meaning

        subLayout.addWidget(self.character_btn, 3, 0, 3, 6) # current word

        subLayout.addWidget(self.num_of_characters, 9, 0, 1, 3) # number of remaining characters
        subLayout.addWidget(self.percent_correct, 9, 3, 1, 3) # percent correct

        subLayout.addWidget(self.character_entry_label, 6, 0, 1, 3) # character entry label
        subLayout.addWidget(self.character_entry, 7, 0, 2, 3) # character entry

        subLayout.addWidget(self.meaning_entry_label, 6, 3, 1, 3) # meaning entry label
        subLayout.addWidget(self.meaning_entry, 7, 3, 2, 3) # meaning entry

        self.setWindowTitle('日本語のクイズ')

        self.setLayout(layout)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def reload_button(self):
        confirmation_window = QtWidgets.QMessageBox(self)
        confirmation_window.setWindowTitle('Warning')
        confirmation_window.setText('Are you sure to want to reload quiz csvs? You will need to reselect a quiz.')
        confirmation_window.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmation_button = confirmation_window.exec()
        if confirmation_button == QtWidgets.QMessageBox.Yes:
            self.empty_file_1 = False
            self._define_directories()

            self._load_vocab(self.alphabet_directory, self.alphabet, self.alphabet_name)
            self._load_vocab(self.missed_directory, self.missed, self.missed_name)
            self._load_vocab(self.vocab_directory, self.vocab, self.vocab_name)
            self._load_vocab(self.all_words_directory, self.all_words, self.all_words_name)

            self.prev_meaning.setText('')
            self.prev_kanji.setText('')
            self.character_btn.setText('select a quiz')
            self.character_entry.setText('')
            self.meaning_entry.setText('')
            self.num_of_characters.setText('Characters Remaining: ')
        else:
            pass
        
    def clear_button(self):
        confirmation_window = QtWidgets.QMessageBox(self)
        confirmation_window.setWindowTitle('Warning')
        confirmation_window.setText('Are you sure to want to clear missed words? This will delete all missed words.')
        confirmation_window.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmation_button = confirmation_window.exec()
        if confirmation_button == QtWidgets.QMessageBox.Yes:
            with open(self.missed_words, 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerow(['romaji', 'kanji', 'meaning'])
        else:
            pass

    def selectActivated(self, text):
        self.quiz_text = text
        self.two_column_quiz = False
        self.reversed = False
        self.all = False
        self.prev_meaning.setText('')
        self.prev_kanji.setText('')
        self.percent_correct.setText('Percent Correct: ')

        if text == 'all-words':
            self.all = True
            self.romaji = []
            self.japanese = []
            self.meaning = []
            self.temp_romaji = _np.array(self.all_words[0][0])
            self.temp_japanese = _np.array(self.all_words[0][1])
            self.temp_meaning = _np.array(self.all_words[0][2])

            # add all the kanji not in the counter csv
            for i, j in enumerate(self.temp_japanese):
                if j not in _np.array(self.counter_kanji):
                    self.romaji = _np.append(self.romaji, self.temp_romaji[i])
                    self.japanese = _np.append(self.japanese, self.temp_japanese[i])
                    self.meaning = _np.append(self.meaning, self.temp_meaning[i])
            # add all the kanji that have not been quizzed in a set amount of time
            for i, j in enumerate(self.counter_kanji):
                if self.counter_time[i] + self.interval_time * 2 ** int(self.counter_counter[i]) < self.current_time:
                    for kk, ll in enumerate(self.temp_japanese):
                        if j == ll:
                            self.romaji = _np.append(self.romaji, self.temp_romaji[kk])
                            self.japanese = _np.append(self.japanese, self.temp_japanese[kk])
                            self.meaning = _np.append(self.meaning, self.temp_meaning[kk])
            self.missed_file = self.missed_words

        if text == 'all-words-newest-25':
            self.romaji = _np.array(self.all_words[0][0][-25:])
            self.japanese = _np.array(self.all_words[0][1][-25:])
            self.meaning = _np.array(self.all_words[0][2][-25:])
            self.missed_file = self.missed_words

        for i in self.alphabet_name:
            if text == i:
                index = self.alphabet_name.index(i)
                self.romaji = _np.array(self.alphabet[index][0])
                self.japanese = _np.array(self.alphabet[index][1])
                self.two_column_quiz = True
                break

        for i in self.vocab_name:
            if text == i:
                index = self.vocab_name.index(i)
                self.romaji = _np.array(self.vocab[index][0])
                self.japanese = _np.array(self.vocab[index][1])
                self.meaning = _np.array(self.vocab[index][2])
                self.missed_file = self.missed_words
                break

        for i in self.missed_name:
            if text == i:
                index = self.missed_name.index(i)
                if self.empty_file_1 == True:
                    self.num_of_characters.setText('Characters Remaining: ')
                    self.percent_correct.setText('Percent Correct: ')
                    self.character_btn.setText('empty quiz')
                    self.question_status.setText('')
                    return
                else:
                    self.romaji = _np.array(self.missed[index][0])
                    self.japanese = _np.array(self.missed[index][1])
                    self.meaning = _np.array(self.missed[index][2])
                    self.missed_file = self.missed_words
                    if self.romaji.size == 1:
                        self.num_of_characters.setText('Characters Remaining: ')
                        self.percent_correct.setText('Percent Correct: ')
                        self.character_btn.setText('one word quiz')
                        self.question_status.setText('')
                        return
                break

        self.button_init()

        if self.two_column_quiz:
            self.romaji, self.japanese = shuffle(self.romaji, self.japanese)
        else:
            self.romaji, self.japanese, self.meaning = shuffle(self.romaji, self.japanese, self.meaning)

        self.total_number = self.japanese.size
        self.num_of_characters.setText('Characters Remaining: ' + str(self.japanese.size) + '/' + str(self.total_number))
        self.character_btn.setText(self.japanese[1])

    def button_init(self):
        self.character_entry.setText('')
        self.meaning_entry.setText('')
        self.question_status.setText('')
        self.character_entry.setFocus()
        self.num_correct = 0
        self.num_total = 0

    def storeValue(self):
        self.character_entry.setFocus()
        self.text_romaji = self.character_entry.text()
        self.text_meaning = self.meaning_entry.text()

        # if quizzing one of the alphabet quizzes
        if self.two_column_quiz:
            self.two_column_store()

        if not self.two_column_quiz:
            self.three_column_store()

    def two_column_store(self):
        # if there is only one word left in the quiz
        if self.japanese.size == 1:
            # correct answer is given
            if self.text_romaji in self.romaji[0].split() or self.text_romaji == self.romaji[0]:
                self.quiz_is_done()
            # you get the question wrong
            else:
                self.prev_kanji.setStyleSheet("color: red;")
                self.prev_meaning.setStyleSheet("color: red;")
                self.prev_kanji.setText(str(self.japanese[0]))
                self.prev_meaning.setText(str(self.romaji[0]))
                self.character_entry.setText('')
                self.meaning_entry.setText('')
        # more than one word left in the quiz
        else:
            self.num_total += 1
            # correct answer is given
            if self.text_romaji in self.romaji[1].split() or self.text_romaji == self.romaji[1]:
                self.num_correct += 1
                self.prev_kanji.setStyleSheet("color: green;")
                self.prev_meaning.setStyleSheet("color: green;")
                self.prev_kanji.setText(str(self.japanese[1]))
                self.prev_meaning.setText(str(self.romaji[1]))
                self.japanese = _np.delete(self.japanese, 1)
                self.romaji = _np.delete(self.romaji, 1)
            # you get the question wrong
            else:
                self.prev_kanji.setStyleSheet("color: red;")
                self.prev_meaning.setStyleSheet("color: red;")
                self.prev_kanji.setText(str(self.japanese[1]))
                self.prev_meaning.setText(str(self.romaji[1]))
                self.romaji, self.japanese = shuffle(self.romaji, self.japanese)
            # check how many are left
            if self.japanese.size == 1:
                self.character_btn.setText(self.japanese[0])
            else:
                self.character_btn.setText(self.japanese[1])
            self.character_entry.setText('')
            self.meaning_entry.setText('')
            self.num_of_characters.setText('Characters Remaining: ' + str(self.japanese.size) + '/' + str(self.total_number))
            self.percent_correct.setText('Percent Correct: ' + str(round(self.num_correct/self.num_total * 100, 2)) + '%')

    def three_column_store(self):
        # if there is only one word left in the quiz
        if self.japanese.size == 1:
            # correct answer is given
            if (self.text_romaji in self.romaji[0].split() or self.text_romaji == self.romaji[0]) and \
                (self.text_meaning in self.meaning[0].split() or self.text_meaning == self.meaning[0]):
                self.quiz_is_done()
            # you get the question wrong
            else:
                self.prev_kanji.setStyleSheet("color: red;")
                self.prev_meaning.setStyleSheet("color: red;")
                self.prev_kanji.setText(str(self.japanese[0]))
                self.prev_meaning.setText(str(self.romaji[0]) + '\n' + str(self.meaning[0]))
                self.character_entry.setText('')
                self.meaning_entry.setText('')
        # there is more than one word left in the quiz
        else:
            self.num_total += 1
            # correct answer is given
            if (self.text_romaji in self.romaji[1].split() or self.text_romaji == self.romaji[1]) and \
                (self.text_meaning in self.meaning[1].split() or self.text_meaning == self.meaning[1]):
                self.num_correct += 1
                self.prev_kanji.setStyleSheet("color: green;")
                self.prev_meaning.setStyleSheet("color: green;")
                self.prev_kanji.setText(str(self.japanese[1]))
                self.prev_meaning.setText(str(self.romaji[1]) + '\n' + str(self.meaning[1]))
                if self.all:
                    if self.japanese[1] in _np.array(self.counter_kanji):
                        for i, j in enumerate(self.counter_kanji):
                            if j == self.japanese[1]:
                                self.counter_counter[i] = int(self.counter_counter[i]) + 1
                                self.counter_time[i] = time.time()
                    else:
                        self.counter_kanji = _np.append(self.counter_kanji, self.japanese[1])
                        self.counter_counter  = _np.append(self.counter_counter, '1')
                        self.counter_time  = _np.append(self.counter_time, time.time())
                self.japanese = _np.delete(self.japanese, 1)
                self.romaji = _np.delete(self.romaji, 1)
                self.meaning = _np.delete(self.meaning, 1)
            # you get the question wrong
            else:
                self.prev_kanji.setStyleSheet("color: red;")
                self.prev_meaning.setStyleSheet("color: red;")
                self.prev_kanji.setText(str(self.japanese[1]))
                self.prev_meaning.setText(str(self.romaji[1]) + '\n' + str(self.meaning[1]))
                if self.all:
                    for i, j in enumerate(self.counter_kanji):
                        if j == self.japanese[1]:
                            self.counter_kanji = _np.delete(self.counter_kanji, i)
                            self.counter_counter  = _np.delete(self.counter_counter, i)
                            self.counter_time  = _np.delete(self.counter_time, i)
                # add the missed word to the missed_file csv
                with open(self.missed_file, 'a', encoding='utf-8', newline='') as csvfile:
                    fieldnames = ['romaji', 'japanese', 'meaning']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'romaji': str(self.romaji[1]), 'japanese': str(self.japanese[1]), 'meaning': str(self.meaning[1])})
                self.romaji, self.japanese, self.meaning = shuffle(self.romaji, self.japanese, self.meaning)
            # check how many words are left
            if self.japanese.size == 1:
                self.character_btn.setText(self.japanese[0])
            else:
                self.character_btn.setText(self.japanese[1])
            self.character_entry.setText('')
            self.meaning_entry.setText('')
            self.num_of_characters.setText('Characters Remaining: ' + str(self.japanese.size) + '/' + str(self.total_number))
            self.percent_correct.setText('Percent Correct: ' + str(round(self.num_correct/self.num_total * 100, 2)) + '%')
            # write the updated dataframe to the counter.csv
            if self.all:
                d = {'kanji': self.counter_kanji,  'counter': self.counter_counter, 'time': self.counter_time}
                df = _pd.DataFrame(d)
                df.to_csv('counters/counter.csv', sep=',', header=True, index=False)

    def quiz_is_done(self):
        self.prev_meaning.setStyleSheet("color: green;")
        self.prev_meaning.setText('All done!')
        self.prev_kanji.setText('')
        self.character_btn.setText(':D')
        self.character_entry.setText('')
        self.meaning_entry.setText('')
        self.num_of_characters.setText('Go Again!')

    def closeEvent(self, x):
        print('This does something')
        self.stop = True
        self.reactor.stop()


if __name__ == '__main__':
    a = QtWidgets.QApplication([])
    import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    client = Quiz(reactor)
    client.show()
    reactor.run()
