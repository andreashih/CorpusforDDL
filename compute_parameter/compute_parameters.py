from collections import Counter
import pickle
import pandas as pd
import re

# 讀入 COCT txt 檔
coct_path = '../data/coct_frequency_list_2019.txt'
with open(coct_path) as f:
    lines = f.readlines()
    lines = [line.rstrip('\n') for line in lines]

coct_data = [x.split('\t') for x in lines[5:len(lines)-2]]
keys = [x[1] for x in coct_data]
vals = [int(x[2]) for x in coct_data]
coct_data_dict = dict(list(zip(keys, vals)))

# with open('../data/coct_data_dict.pkl', 'wb') as f:
#     pickle.dump(coct_data_dict, f)

# 參考國教院詞語分級表
naer_word_list = pd.read_excel('../data/臺灣華語文能力基準詞語表_111-09-20.xlsx')
naer_word_list = naer_word_list.assign(word_1=naer_word_list['詞語'].str.split('/')).explode('詞語')
naer_word_list = naer_word_list.explode('word_1') # 把用 / 連接的詞語切開做成新的一列
levels = naer_word_list['級別'].values
word_level_dict = pd.Series(levels, index=naer_word_list['word_1']).to_dict()

# with open('../data/word_level_dict.pkl', 'wb') as f:
#     pickle.dump(word_level_dict, f)

# 高頻詞與低頻詞
def get_high_low_freq(sentence):

  freq = []
  for word in sentence:
    try:
      f = coct_data_dict[word]
    except:
      f = 0 # 若是在 coct_data_dict 中找不到該詞的頻率資料，則將其頻率指定為 0
    freq.append(f)

  high_low = ['High' if f > 100 else 'Low' for f in freq] # 若在 ASBC 中詞頻大於 100，則視為高頻詞 (High)

  return dict(Counter(high_low))

# 詞頻
def get_word_freq(sentence):

  word_freq = []

  for word in sentence:
    try:
      freq = coct_data_dict[word]
    except:
      freq = 'Unknown'
    res = f'{word}({freq})'
    word_freq.append(res)

  word_freq = ' '.join(word_freq)

  return word_freq

# 詞彙等級
def get_word_level(sentence):

  levels = []
  for word in sentence:
    try:
      level = word_level_dict[word]
    except:
      level = 'Unknown' # 如果找不到該詞彙，級別設為 Unknown
    levels.append(level)
  
  return dict(Counter(levels))

# 詞彙長度
def get_long_word_count(sentence):

  long_word_count = 0
  for word in sentence:
    if len(word) >= 3:
      long_word_count += 1
  
  return long_word_count

# 完整的句子
def get_complete_sentence(sentence):

  if re.search(r'。|？|！', sentence) and 'V' in sentence:
    res = 'Y'
  else:
    res = 'N'

  return res

# 完整的語境
def get_complete_context(sentence):

  if re.search(r'Caa|Cab|Cba|Cbb', sentence):
    res = 'Y'
  else:
    res = 'N'

  return res

# black list
def get_blacklist(sentence):

  chinese_num_upper = r'[零壹貳參肆伍陸柒捌玖拾佰仟]{8}'
  chinese_num_lower = r'[○一二三四五六七八九十廿百千]{8}' 
  url = r'(www|http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'

  check_chinese_num_upper = re.search(chinese_num_upper, sentence)
  check_chinese_num_lower = re.search(chinese_num_lower, sentence)
  check_digit = re.search(r'[0-9]{8}', sentence)
  check_url = re.search(url, sentence)

  if check_chinese_num_upper or check_chinese_num_lower or check_digit or check_url:
    res = 'Y'
  else:
    res = 'N'

  return res

# grey list
def get_greylist(sentence):

  if re.search(r'Nb', sentence):
    res = 'Y'
  else:
    res = 'N'

  return res