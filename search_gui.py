import Tkinter
from Tkinter import *
import search

global query
query = ""
class SearchApplication():

    def __init__(self):
        self._search_window = Tkinter.Tk()


    def start(self):
        global E1
        L1 = Label(self._search_window, text="Query:")
        L1.grid(row=0, column=0)
        E1 = Entry(self._search_window, bd = 5)
        E1.grid(row=0, column=1)

        MyButton1 = Button(self._search_window, text="Search", width=10, command=search.run_query_program(SearchApplication().getQuery))
        MyButton1.grid(row=1, column=1)
        self._search_window.mainloop()

    def getQuery(self):
        print ("HI",E1.get())
        return E1.get()



    def _on_search_button(self):
        return

    def _display_results(urls):
        return


if __name__ == '__main__':
    SearchApplication().start()
