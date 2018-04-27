import praw
import time
from bs4 import BeautifulSoup
import urllib.request
import re
from praw_info import client_id, client_secret, username, password, user_agent

sauce = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_fallacies').read()
soup = BeautifulSoup(sauce, 'lxml')

reddit = praw.Reddit(client_id='client_id',
                     client_secret='client_secret',
                     username='username',
                     password='password',
                     user_agent='user_agent')

fallacies = []

for line in soup.find_all('li'):
    if line.get('title') is not 'None':
        if len(line.find_all('a')) > 1:
            fallacies.append(str(line.find_all('a')[0].get('title')))
        else:
            for x in line.find_all('a'):
                fallacies.append(str(x.get('title')))

# fallacies = fallacies[12:148]
fallacies = [x for x in fallacies[12:148] if x != 'None']


def find_fallacy():
    authors = []
    for submission in reddit.subreddit('debatereligion').new(limit=10):

        submission.comments.replace_more()

        for comment in submission.comments.list():
            for fallacy in fallacies:
                # if re.search(fallacy, comment.body, re.IGNORECASE):     - another way to look for the word in the comment
                if fallacy.lower() in comment.body.lower():
                    authors.append(comment.author)
                    # print(comment.body)
    return authors

dirty_dic = {}
fallacy_lords = {}
fallacious_authors = find_fallacy()


if __name__ == '__main__':
    while True:
        for author in fallacious_authors:
            dirty_count = 0
            sub_count = 0
            trashy_score = 0
            dirty_dic[author] = [{}, dirty_count, sub_count]
            for comment in reddit.redditor(str(author)).comments.new():
                calc = 0
                dirty = False
                for fallacy in fallacies:
                    # if re.search(fallacy, comment.body, re.IGNORECASE):     - another way to look for the word in the comment
                    if fallacy.lower() in comment.body.lower():
                        if comment.id not in dirty_dic:
                            dirty = True
                            dirty_dic[author][0][comment.id] = [comment.body]
                            calc += 1
                            dirty_dic[author][0][comment.id].append(calc)          #this can be used to store the dirty count
                        else:                                                      #in every comment.
                            dirty = True
                            calc += 1
                            dirty_dic[author][0][comment.id].append(calc) 
                if dirty:
                    dirty_dic[author][1] += 1
                    dirty_count += 1
                dirty_dic[author][2] += 1
                sub_count += 1


            try:
                trashy_score = dirty_count / sub_count
            except: trashy_score == 0

            with open('trashyscore.txt', 'r') as file:
                posted_score = file.read()
                if str(author) not in posted_score:
                    with open('trashyscore.txt', 'a') as file:
                        message = 'User {} fallacy score is: {} \n'.format(str(author), trashy_score)
                        file.write(str(time.ctime(int(time.time()))))
                        file.write('\n')
                        file.write(message)
                        file.write('\n')
                        file.write('\n')

            if trashy_score >= 0.05:
                fallacy_lords[str(author)] = [trashy_score]

                message2 = 'fallacy lord: {} has a trashy score of {}' \
                           'and {} comments are dirty out of {} total'.format(str(author),
                                                                              fallacy_lords[str(author)],
                                                                              dirty_dic[author][1],
                                                                              dirty_dic[author][2])

            # message2 = 'here are the top 3 newest comments by user: {} \n {}'.format(str(author), dirty_dic[author][0][:3])
            # print(message2)

            if str(author) in fallacy_lords:
                with open('fallacylords.txt', 'r') as f:
                    already_posted = f.read()
                    if str(author) not in already_posted:
                        with open('fallacylords.txt', 'a') as file:
                            file.write(time.ctime(int(time.time())))
                            file.write('\n')
                            file.write(message2)
                            file.write('\n')
                            file.write('\n')
                        print(str(author))
        print('\n \n sleeping for 1 hour before looking for more fallacy lords \n', time.ctime(int(time.time())), '\n \n')
        time.sleep(60*60)
