import os, sys, argparse, torch, pickle, random, json, numpy as np
from os.path import abspath, dirname, join, exists
from sys import stdout
from scipy.special import softmax


from copy import deepcopy 

# # test function
curpath = dirname(abspath(__file__))
upperpath = dirname(curpath)
sys.path.append(upperpath)
from instance import Rel_Instance, Span_Instance
from config import label2ind, ind2label
from eval import test_eval, instance_level_eval

def combine_prediction(targets, components, rels, a = 0.5):

    target2containerScore = {t.span_id: t.pred_score for t in targets}
    component2containeeScore = {c.span_id: c.pred_score for c in components}
    new_rels = [deepcopy(rel) for rel in rels] 

    for rel in new_rels:   
        scores = np.array(rel.pred_score) * (np.array(target2containerScore[rel.span1.span_id]) + np.array(component2containeeScore[rel.span2.span_id]))
        scores = softmax(scores)
        
        if scores[0] > scores[1]:
            rel.pred_relation_label = 'Contains'
        else:
            rel.pred_relation_label = 'O'
        
    return new_rels

if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    
    parser.add_argument("-components",required = True)
    parser.add_argument("-targets",required = True)
    parser.add_argument("-rels",required = True)

    parser.add_argument("-gold_rels",required = True)

    parser.add_argument("-a",type = float, default = 0.5)

    args = parser.parse_args()

    components = pickle.load(open(args.components, "rb"))
    targets = pickle.load(open(args.targets, "rb"))
    rels = pickle.load(open(args.rels, "rb"))

    gold_rels = pickle.load(open(args.gold_rels, "rb"))


    new_rels = combine_prediction(targets, components, rels, a = args.a)

    precision, recall, f1 = test_eval(new_rels, gold_rels, "Contains")
    print(f"TUPLE-LEVEL EVAL of combined prediction: precison: {precision*100:.2f}, recall: {recall*100:.2f}, f1: {f1*100:.2f}")

    precision, recall, f1 = instance_level_eval(new_rels, gold_rels, "Contains")
    print(f"INSTANCE-LEVEL EVAL of combined prediction: precision: {precision*100:.2f}, recall: {recall*100:.2f}, f1: {f1*100:.2f}")