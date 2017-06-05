from Tkinter import *
import search

import webbrowser


class SearchApplication():


    def __init__(self):
        self._search_window = Tk()
        self._search_window.title("CGY Search Engine")


    def start(self):
        global E1
        L1 = Label(self._search_window, text="Query:")
        L1.grid(row=0, column=0)
        E1 = Entry(self._search_window, bd = 5)
        E1.grid(row=0, column=1)

        MyButton1 = Button(master=self._search_window, text="Search", width=10, command=self._on_search_button)
        MyButton1.grid(row=1, column=1)
        self._search_window.mainloop()

    def _get_query(self):
        print ("hi", E1.get())
        return E1.get()


    def _on_search_button(self):
        query = self._get_query()
        urls = search.run_query_program_with_params(query)
        if (hasattr(self, "_results_window")):
            self._results_window.destroy()
        self._display_results(urls)

    def _display_results(self, urls):
        self._results_window = Tk()
        self._results_window.title("Search Results")
        self._results_window.minsize(300, 300)
        counter = 1
        for url in urls:
            button_text = str(counter) + ": "+ url
            button = Button(master=self._results_window, text=button_text, command=lambda u=url:self._on_click_result(u))
            button.grid(row=counter-1, column=0)
            counter += 1


    def _on_click_result(self, url):
        webbrowser.open("http://" + url)


if __name__ == '__main__':
    SearchApplication().start()
