# PA7, CS124, Stanford
# v.1.0.4
#
# Original Python code by Ignacio Cases (@cases)
######################################################################
import util

import numpy as np
import re


# noinspection PyMethodMayBeStatic
class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
        # The chatbot's default name is `moviebot`.
        # TODO: Give your chatbot a new name.
        self.name = 'moviebot'
        
        self.creative = creative

        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titles, ratings = util.load_ratings('data/ratings.txt')
        self.sentiment = util.load_sentiment_dictionary('data/sentiment.txt')

        ########################################################################
        # TODO: Binarize the movie ratings matrix.                             #
        ########################################################################
        
        # Binarize the movie ratings before storing the binarized matrix.
        self.ratings = ratings
        self.binarize(self.ratings, .5)
        self.movie_list = []
        self.opin = 0
        self.fine_grained = util.load_sentiment_dictionary('data/fine_grained.txt')
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

    ############################################################################
    # 1. WARM UP REPL                                                          #
    ############################################################################

    def greeting(self):
        """Return a message that the chatbot uses to greet the user."""
        ########################################################################
        # TODO: Write a short greeting message                                 #
        ########################################################################

        greeting_message = "Welcome! My name is the Film Recommendation Bot. I will ask for five movies, one at a time, and how you feel about them. Then I can recommend you a movie you may enjoy. Please spell the movie's title correctly and put it in quotations when giving me your opinions on five movies."

        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################
        return greeting_message

    def goodbye(self):
        """
        Return a message that the chatbot uses to bid farewell to the user.
        """
        ########################################################################
        # TODO: Write a short farewell message                                 #
        ########################################################################

        goodbye_message = "I hope you enjoy your movie and chatting with me was enjoyable!"

        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return goodbye_message

    ############################################################################
    # 2. Modules 2 and 3: extraction and transformation                        #
    ############################################################################

    def process(self, line):
        """Process a line of input from the REPL and generate a response.

        This is the method that is called by the REPL loop directly with user
        input.

        You should delegate most of the work of processing the user's input to
        the helper functions you write later in this class.

        Takes the input string from the REPL and call delegated functions that
          1) extract the relevant information, and
          2) transform the information into a response to the user.

        Example:
          resp = chatbot.process('I loved "The Notebook" so much!!')
          print(resp) // prints 'So you loved "The Notebook", huh?'

        :param line: a user-supplied line of text
        :returns: a string containing the chatbot's response to the user input
        """
        ########################################################################
        # TODO: Implement the extraction and transformation in this method,    #
        # possibly calling other functions. Although your code is not graded   #
        # directly based on how modular it is, we highly recommended writing   #
        # code in a modular fashion to make it easier to improve and debug.    #
        ########################################################################
#        if self.creative:
#            response = "I processed {} in creative mode!!".format(line)
#        else:
#            response = "I processed {} in starter mode!!".format(line)
        response = ''
        # initial processing
        preprocessed = self.preprocess(line)
#        print(preprocessed)
        title_list = self.extract_titles(preprocessed)
        # print(title_list)
        movies = self.find_movies_by_title(title_list)
        # print(movies)
        opinion = self.extract_sentiment(preprocessed)
#        print(opinion)

        # disambiguate (after given clarification)
        if len(self.movie_list) >0:
            print(self.movie_list)
            # print(preprocessed)
            narrowed_down = self.disambiguate(preprocessed, self.movie_list)
            # need to disambiguate again
            if len(narrowed_down) > 1:
                self.movie_list = narrowed_down
                response = "Which movie did you mean? Please give me the year in quotations. "
                for i in range(len(narrowed_down)):
                    response += '%s, ' %self.titles[narrowed_down[i]][0]
            # we have our answer
            else:
                movies = narrowed_down
                opinion = self.opin
                # print(movies)
                # self.movie_list = []
                # self.opin = 0

        #first time there's multiple movies
        if len(movies) > 1 and len(self.movie_list) == 0:
            self.movie_list = movies
            self.opin = opinion
            
            response = "Which movie did you mean? Please give me the year in quotations. "
            for i in range(len(movies)):
                response += '%s, ' %self.titles[movies[i]][0]

        # print("line 142 :", movies)
        if len(movies)>0:
            movie = movies[0]
        # print(self.titles[movies[0]])
        emotion_neg_words = ['Upset', 'Sad', 'Angry', 'Tired', 'Frustrated', 'Lonely', 'Nervous', 'Hurt', 'Confused', 'Overwhelmed', 'Insecure', 'Jealous', 'Worried', 'Disappointed', 'Hopeless', 'Miserable', 'Enraged', 'Fearful']
        emotion_pos_words = ['Happy',  'Excited', 'Hopeful', 'Proud', 'Glad', 'Loved', 'Surprised', 'Calm', 'Relaxed', 'Grateful', 'Appreciated', 'Determined', 'Empowered']

        # doing the opinions to give final confirmation
        if opinion == 1 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
            response = "So you like %s, huh?" % self.titles[movie][0]
        elif opinion == -1 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
            response = "So you didn't like %s, huh?" % self.titles[movie][0]
        elif len(movies) == 0 and response == '' and len(self.movie_list) != 1:
            for word in emotion_neg_words:
                word = word.lower()
                if word in preprocessed:
                    response = "Oh! Did I make you %s? I'm sorry!" %word
            for word in emotion_pos_words:
                word = word.lower()
                if word in preprocessed:
                    response = "Oh! I made you %s? I'm glad!" %word
            if 'Can you' in preprocessed:
                response = "I'm sorry, I can't %s. I am a movie-recommendation bot." % preprocessed[preprocessed.rindex('Can you')+7:]
            elif 'What is' in preprocessed:
                response = "I'm sorry, I don't know the answer to %s. I am a movie-recommendation bot." % preprocessed
            elif response == '':
                response = "Hm, that's not really what I want to talk about now, let's go back to movies."
        elif opinion == 0 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
            response = "So you have mixed opinions on %s, huh?" % self.titles[movie][0]
        # print('length:', len(self.movie_list))
        if opinion == 2 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
            response = "So you love %s, huh?" % self.titles[movie][0]
        elif opinion == -2 and response == '' and len(self.movie_list) != 1 and len(movies) != 0:
            response = "So you hate %s, huh?" % self.titles[movie][0]
        # zeroing out the record keeping because we have our movie
        if len(movies) == 1:
            self.opin = 0
            self.movie_list = []
        # print(self.movie_list)
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return response

    @staticmethod
    def preprocess(text):
        """Do any general-purpose pre-processing before extracting information
        from a line of text.

        Given an input line of text, this method should do any general
        pre-processing and return the pre-processed string. The outputs of this
        method will be used as inputs (instead of the original raw text) for the
        extract_titles, extract_sentiment, and extract_sentiment_for_movies
        methods.

        Note that this method is intentially made static, as you shouldn't need
        to use any attributes of Chatbot in this method.

        :param text: a user-supplied line of text
        :returns: the same text, pre-processed
        """
        ########################################################################
        # TODO: Preprocess the text into a desired format.                     #
        # NOTE: This method is completely OPTIONAL. If it is not helpful to    #
        # your implementation to do any generic preprocessing, feel free to    #
        # leave this method unmodified.                                        #
        ########################################################################
        # sentence_list = []
        # word = ''
        for i in range(len(text)):
            if text[i-1] == '"':
                text[i].upper()
            if text[i-1] != '"':
                text[i].lower()
#            print(text)
#             if text[i] == ' ':
#                 sentence_list.append(word)
#                 word = ''
#             if text[i] != ' ':
# #                print(text[i])
#                 word += text[i]
#         if text[-1] != ' ':
# #            print("made it")
#             sentence_list.append(word)
#            print(sentence_list)
        ########################################################################
        #                             END OF YOUR CODE                         #
        ########################################################################

        return text

    def extract_titles(self, preprocessed_input):
        """Extract potential movie titles from a line of pre-processed text.

        Given an input text which has been pre-processed with preprocess(),
        this method should return a list of movie titles that are potentially
        in the text.

        - If there are no movie titles in the text, return an empty list.
        - If there is exactly one movie title in the text, return a list
        containing just that one movie title.
        - If there are multiple movie titles in the text, return a list
        of all movie titles you've extracted from the text.

        Example:
          potential_titles = chatbot.extract_titles(chatbot.preprocess(
                                            'I liked "The Notebook" a lot.'))
          print(potential_titles) // prints ["The Notebook"]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: list of movie titles that are potentially in the text
        """
        list_of_films = []
        # title = ''
        # tracker = 0
        # for word in preprocessed_input:
        #     if tracker == 1:
        #         if word[-1] =='"':
        #             tracker -= 0
        #             list_of_films.append(title)
        #             title = ''
        #         else:
        #             title = title + " " + elem
        #     elif word[0] == '"':
        #         tracker += 1
        #         if word[-1] == '"':
        #             list_of_films.append(word[1:-1])
        #             tracker -= 1
        # print(preprocessed_input)
        regex = '"\w+\s*\w*"'
        list_of_films = re.findall(regex, preprocessed_input)
        # print(list_of_films[0])
        # list_of_films = ' '.join(list_of_films)
        # print(list_of_films)
        return list_of_films

    def find_movies_by_title(self, title):
        """ Given a movie title, return a list of indices of matching movies.

        - If no movies are found that match the given title, return an empty
        list.
        - If multiple movies are found that match the given title, return a list
        containing all of the indices of these matching movies.
        - If exactly one movie is found that matches the given title, return a
        list
        that contains the index of that matching movie.

        Example:
          ids = chatbot.find_movies_by_title('Titanic')
          print(ids) // prints [1359, 2716]

        :param title: a string containing a movie title
        :returns: a list of indices of matching movies
        """
        results = []
        for elem in title:
            # print(elem)
            elem = elem[1:-1]
#            print(self.titles)
            for i in range(len(self.titles)):
                # print(self.titles[i])
                if elem in self.titles[i][0]:
                    results.append(i)
                # elif elem.startswith('The'):
                #     print('made it here')
                #     ele = elem[3:] + ', The'
                #     if ele in self.titles[i][0]:
                #         results.append(i)
                # elif elem.startswith('A'):
                #     ele = elem[3:] + ', A'
                #     if ele in self.titles[i][0]:
                #         results.append(i)
                # elif elem.startswith('An'):
                #     ele = elem[3:] + ', An'
                #     if ele in self.titles[i][0]:
                #         results.append(i)

        return results

    def extract_sentiment(self, preprocessed_input):
        """Extract a sentiment rating from a line of pre-processed text.

        You should return -1 if the sentiment of the text is negative, 0 if the
        sentiment of the text is neutral (no sentiment detected), or +1 if the
        sentiment of the text is positive.

        As an optional creative extension, return -2 if the sentiment of the
        text is super negative and +2 if the sentiment of the text is super
        positive.

        Example:
          sentiment = chatbot.extract_sentiment(chatbot.preprocess(
                                                    'I liked "The Titanic"'))
          print(sentiment) // prints 1

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a numerical value for the sentiment of the text
        """

        if self.creative == False:

            sentiment = 0
            negation_words = ['no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nor', 'without', 'cannot', 'won\'t', 'don\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t', 'shouldn\'t', 'wouldn\'t', 'couldn\'t', 'mightn\'t', 'needn\'t', 'rarely', 'scarcely', 'seldom', 'hardly', 'barely', 'refuse']

            preprocessed_input = preprocessed_input.split(' ')

            for word in preprocessed_input:
                if word in self.sentiment:
                    if self.sentiment[word] == 'pos':
                        sentiment += 1
                    if self.sentiment[word] == 'neg':
                        sentiment -= 1
                if word[:-1] in self.sentiment:
                    if self.sentiment[word[:-1]] == 'pos':
                        sentiment += 1
                    if self.sentiment[word[:-1]] == 'neg':
                        sentiment -= 1
            for elem in negation_words:
                if elem in preprocessed_input:
                    sentiment = sentiment * -1

            if sentiment > 0:
                return 1
            elif sentiment < 0:
                return -1
            else:
                return 0

        
        elif self.creative == True:

            sentiment = 0
            negation_words = ['no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nor', 'without', 'cannot', 'won\'t', 'don\'t', 'didn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t', 'shouldn\'t', 'wouldn\'t', 'couldn\'t', 'mightn\'t', 'needn\'t', 'rarely', 'scarcely', 'seldom', 'hardly', 'barely', 'refuse']
            intensification = ['really', 'somewhat']

            preprocessed_input = preprocessed_input.split(' ')

            for word in preprocessed_input:
                if word in self.fine_grained:
                    sentiment += int(self.fine_grained[word])
                if word[:-1] in self.fine_grained:
                    sentiment += int(self.fine_grained[word[:-1]])

            for elem in negation_words:
                if elem in preprocessed_input:
                    sentiment = sentiment * -1
                
            if 'really' in preprocessed_input:
                sentiment = sentiment * 2
                
            if 'somewhat' in preprocessed_input:
                sentiment = sentiment / 2
            # print(sentiment)
            if sentiment == 0:
                return 0
            if sentiment <= 1 and sentiment > 0:
                return 1
            if sentiment >= -1 and sentiment < 0:
                return -1
            if sentiment > 1:
                return 2
            if sentiment < -1:
                return -2
                    


    def extract_sentiment_for_movies(self, preprocessed_input):
        """Creative Feature: Extracts the sentiments from a line of
        pre-processed text that may contain multiple movies. Note that the
        sentiments toward the movies may be different.

        You should use the same sentiment values as extract_sentiment, described

        above.
        Hint: feel free to call previously defined functions to implement this.

        Example:
          sentiments = chatbot.extract_sentiment_for_text(
                           chatbot.preprocess(
                           'I liked both "Titanic (1997)" and "Ex Machina".'))
          print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

        :param preprocessed_input: a user-supplied line of text that has been
        pre-processed with preprocess()
        :returns: a list of tuples, where the first item in the tuple is a movie
        title, and the second is the sentiment in the text toward that movie
        """
        pass

    def find_movies_closest_to_title(self, title, max_distance=3):
        """Creative Feature: Given a potentially misspelled movie title,
        return a list of the movies in the dataset whose titles have the least
        edit distance from the provided title, and with edit distance at most
        max_distance.

        - If no movies have titles within max_distance of the provided title,
        return an empty list.
        - Otherwise, if there's a movie closer in edit distance to the given
        title than all other movies, return a 1-element list containing its
        index.
        - If there is a tie for closest movie, return a list with the indices
        of all movies tying for minimum edit distance to the given movie.

        Example:
          # should return [1656]
          chatbot.find_movies_closest_to_title("Sleeping Beaty")

        :param title: a potentially misspelled title
        :param max_distance: the maximum edit distance to search for
        :returns: a list of movie indices with titles closest to the given title
        and within edit distance max_distance
        """

        pass

    def disambiguate(self, clarification, candidates):
        """Creative Feature: Given a list of movies that the user could be
        talking about (represented as indices), and a string given by the user
        as clarification (eg. in response to your bot saying "Which movie did
        you mean: Titanic (1953) or Titanic (1997)?"), use the clarification to
        narrow down the list and return a smaller list of candidates (hopefully
        just 1!)

        - If the clarification uniquely identifies one of the movies, this
        should return a 1-element list with the index of that movie.
        - If it's unclear which movie the user means by the clarification, it
        should return a list with the indices it could be referring to (to
        continue the disambiguation dialogue).

        Example:
          chatbot.disambiguate("1997", [1359, 2716]) should return [1359]

        :param clarification: user input intended to disambiguate between the
        given movies
        :param candidates: a list of movie indices
        :returns: a list of indices corresponding to the movies identified by
        the clarification
        """
        ls = []
        for i in range(len(candidates)):
            # print(self.titles[candidates[i]][0])
            # print(clarification[1:-1])
            if clarification[1:-1] in self.titles[candidates[i]][0]:
                # print(self.titles[candidates[i]][0])
                # print('made it here')
                ls.append(candidates[i])
        return ls
        # narrowed_down = []
        # for word in clarification:
        #     for i in range(len(candidates)):
        #         if word == candidates[i]:
        #             narrowed_down.append(word)
        # return narrowed_down
    ############################################################################
    # 3. Movie Recommendation helper functions                                 #
    ############################################################################

    @staticmethod
    def binarize(ratings, threshold=2.5):
        """Return a binarized version of the given matrix.

        To binarize a matrix, replace all entries above the threshold with 1.
        and replace all entries at or below the threshold with a -1.

        Entries whose values are 0 represent null values and should remain at 0.

        Note that this method is intentionally made static, as you shouldn't use
        any attributes of Chatbot like self.ratings in this method.

        :param ratings: a (num_movies x num_users) matrix of user ratings, from
         0.5 to 5.0
        :param threshold: Numerical rating above which ratings are considered
        positive

        :returns: a binarized version of the movie-rating matrix
        """
        ########################################################################
        # TODO: Binarize the supplied ratings matrix.                          #
        #                                                                      #
        # WARNING: Do not use self.ratings directly in this function.          #
        ########################################################################

        # The starter code returns a new matrix shaped like ratings but full of
        # zeros.
        binarized_ratings = np.zeros_like(ratings)

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return binarized_ratings

    def similarity(self, u, v):
        """Calculate the cosine similarity between two vectors.

        You may assume that the two arguments have the same shape.

        :param u: one vector, as a 1D numpy array
        :param v: another vector, as a 1D numpy array

        :returns: the cosine similarity between the two vectors
        """
        ########################################################################
        # TODO: Compute cosine similarity between the two vectors.             #
        ########################################################################
        similarity = 0
        ########################################################################
        #                          END OF YOUR CODE                            #
        ########################################################################
        return similarity

    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
        """Generate a list of indices of movies to recommend using collaborative
         filtering.

        You should return a collection of `k` indices of movies recommendations.

        As a precondition, user_ratings and ratings_matrix are both binarized.

        Remember to exclude movies the user has already rated!

        Please do not use self.ratings directly in this method.

        :param user_ratings: a binarized 1D numpy array of the user's movie
            ratings
        :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
          `ratings_matrix[i, j]` is the rating for movie i by user j
        :param k: the number of recommendations to generate
        :param creative: whether the chatbot is in creative mode

        :returns: a list of k movie indices corresponding to movies in
        ratings_matrix, in descending order of recommendation.
        """

        ########################################################################
        # TODO: Implement a recommendation function that takes a vector        #
        # user_ratings and matrix ratings_matrix and outputs a list of movies  #
        # recommended by the chatbot.                                          #
        #                                                                      #
        # WARNING: Do not use the self.ratings matrix directly in this         #
        # function.                                                            #
        #                                                                      #
        # For starter mode, you should use item-item collaborative filtering   #
        # with cosine similarity, no mean-centering, and no normalization of   #
        # scores.                                                              #
        ########################################################################

        # Populate this list with k movie indices to recommend to the user.
        recommendations = []

        ########################################################################
        #                        END OF YOUR CODE                              #
        ########################################################################
        return recommendations

    ############################################################################
    # 4. Debug info                                                            #
    ############################################################################

    def debug(self, line):
        """
        Return debug information as a string for the line string from the REPL

        NOTE: Pass the debug information that you may think is important for
        your evaluators.
        """
        debug_info = 'debug info'
        return debug_info

    ############################################################################
    # 5. Write a description for your chatbot here!                            #
    ############################################################################
    def intro(self):
        """Return a string to use as your chatbot's description for the user.

        Consider adding to this description any information about what your
        chatbot can do and how the user can interact with it.
        """
        return """
        Your task is to implement the chatbot as detailed in the PA7
        instructions.
        Remember: in the starter mode, movie names will come in quotation marks
        and expressions of sentiment will be simple!
        TODO: Write here the description for your own chatbot!
        """


if __name__ == '__main__':
    print('To run your chatbot in an interactive loop from the command line, '
          'run:')
    print('    python3 repl.py')
