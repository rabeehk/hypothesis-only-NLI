import pdb
import argparse
import pandas as pd

def get_args():
  parser = argparse.ArgumentParser(description='Evaluate NLI based on prediction files.')
  parser.add_argument('--gold_lbl', type=str, help='The gold train labels file')
  parser.add_argument('--pred_lbl', type=str, help='The predicted labels file')
  parser.add_argument('--hyp_src', type=str, help='File containing the hypothesis sentences')
  #/export/b02/apoliak/nli-hypothes-only/targeted-nli/cl_sprl_
  parser.add_argument('--data_split', type=str, help='Which split of datset is being used')
  parser.add_argument('--preds', type=int, help="Determine whether tosplit based on predictions or not")

  args = parser.parse_args()
  return args

def get_sents(gold_f, pred_f, hyp_f, data_split):
  gold_lbls = open(gold_f).readlines()
  pred_lbls = open(pred_f).readlines()
  hyp_srcs = open(hyp_f).readlines()

  assert (len(gold_lbls) == len(pred_lbls) == len(hyp_srcs))

  sents = {"correct": {}, "wrong": {}}

  correct = {'total': 0}
  tot_lbl = {'total': 0}

  for i in range(len(gold_lbls)):
    gold_lbl = gold_lbls[i].strip()
    if gold_lbl not in tot_lbl:
      tot_lbl[gold_lbl] = 0
    tot_lbl[gold_lbl] += 1
    tot_lbl['total'] += 1

    if gold_lbl == pred_lbls[i].strip():
      correct['total'] += 1
      if gold_lbl not in correct:
        correct[gold_lbl] = 0
      correct[gold_lbl] += 1

      if gold_lbl not in sents["correct"]:
        sents["correct"][gold_lbl] = []
      sents["correct"][gold_lbl].append(hyp_srcs[i].split("|||")[-1].strip())

    else:
      if gold_lbl not in sents["wrong"]:
        sents["wrong"][gold_lbl] = []
      sents["wrong"][gold_lbl].append(hyp_srcs[i].split("|||")[-1].strip())

  return sents

def get_vocab_counts(data, use_preds):
  all_vocab = {}
  vocab_counts = {'correct': {}, 'wrong': {}}
  for key in data:
    for lbl in data[key]:
      if lbl not in vocab_counts[key]:
        vocab_counts[key][lbl] = {}
      for sent in data[key][lbl]:
        for word in sent.split():
          if word not in vocab_counts[key][lbl]:
            vocab_counts[key][lbl][word] = 0
          vocab_counts[key][lbl][word] += 1
          if word not in all_vocab:
            all_vocab[word] = 0
          all_vocab[word] += 1
          
  df = None
  if not use_preds:
    df = pd.DataFrame(columns=['gold-lbl', 'word', 'count'])
    for word in all_vocab:
      for lbl in set(vocab_counts['correct'].keys() + vocab_counts['wrong'].keys()):
        correct, wrong = 0, 0
        if lbl in vocab_counts['correct']:
          if word in vocab_counts['correct'][lbl]:
            correct = vocab_counts['correct'][lbl][word]
        if lbl in vocab_counts['wrong']:
          if word in vocab_counts['wrong'][lbl]:
            wrong = vocab_counts['wrong'][lbl][word]
        count = (correct + wrong) / float(all_vocab[word])
        df = df.append({'gold-lbl': lbl, 'word': word, 'count': count}, ignore_index = True)

    return df, all_vocab

  df = pd.DataFrame(columns=['gold-lbl', 'correct', 'word', 'count'])
  for correct in vocab_counts:
    for lbl in vocab_counts[correct]:
      for word in vocab_counts[correct][lbl]:
        #all_vocab.add(word)
        df = df.append({'gold-lbl': lbl, 'correct': correct, 'word': word, 'count': vocab_counts[correct][lbl][word]}, ignore_index=True)
        
  for correct in vocab_counts:
    for lbl in vocab_counts[correct]:
      for word in all_vocab.difference(vocab_counts[correct][lbl].keys()):
        #print word
        df = df.append({'gold-lbl': lbl, 'correct': correct, 'word': word, 'count': 0}, ignore_index=True)
  

  return df, all_vocab


def main():
  
  args = get_args()

  if args.gold_lbl and args.pred_lbl and args.hyp_src:
    data = get_sents(args.gold_lbl, args.pred_lbl, args.hyp_src, args.data_split)
    df, vocab = get_vocab_counts(data, args.preds)
    pdb.set_trace()
    df.to_pickle("tokens_count.pkl") 


if __name__ == '__main__':
  main()