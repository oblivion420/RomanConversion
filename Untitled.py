#!/usr/bin/env python
# coding: utf-8

# In[68]:


from bs4 import BeautifulSoup
import requests


# In[100]:


response = requests.get("https://tsbp.tgb.org.tw/") 
soup = BeautifulSoup(response.text,"html.parser")
urls = soup.find_all("a")
print(urls)


# In[122]:


import re
p = re.compile('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+')
for url in urls:
    try:
        if re.search('https:\/\/tsbp.tgb.org.tw\/\d+\/\d+\/\S+', url.get("href")):
            print(url.get("href"))
    except:
        pass


# In[105]:





# In[75]:


response = requests.get("https://tsbp.tgb.org.tw/2021/10/eeham.html") 
soup = BeautifulSoup(response.text,"html.parser")


# In[56]:


content = soup.find_all("span", style="font-family: inherit; font-size: medium;")


# In[57]:


for temp in content:
    print(temp.getText())


# In[ ]:





# In[ ]:





# In[ ]:




