import requests
import sys
from flask import Flask, abort, jsonify
from flask.ext.cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/getTargetNames/<source>")
@cross_origin()
def get_target_names(source):
    solr_url = "http://localhost:8983/solr/docs/query?q=type:target AND source:" \
               + source + \
               "&rows=2147483647&wt=json"
    solr_return = requests.get(solr_url).json()

    #valid returned JSON
    if not "response" in solr_return:
        raise Exception("The returned list does not contain response attribute")

    if not "docs" in solr_return["response"]:
        raise Exception("Response attrbute does not contain docs sub-attribute")

    solr_docs = solr_return["response"]["docs"]

    #construct the response in the same format as postgres DB
    return_dict = {};
    return_dict["target_name"] = [];
    for doc in solr_docs:
        if "name" not in doc:
            continue

        return_dict["target_name"].append({
            0: doc["name"]
        })

    return jsonify(return_dict)

@app.route("/getElementNames/<source>")
@cross_origin()
def get_element_names(source):
    solr_url = "http://localhost:8983/solr/docs/query?q=type:element AND source:" \
               + source + \
               "&rows=2147483647&wt=json"
    solr_return = requests.get(solr_url).json()

    # valid returned JSON
    if not "response" in solr_return:
        raise Exception("The returned list does not contain response attribute")

    if not "docs" in solr_return["response"]:
        raise Exception("Response attrbute does not contain docs sub-attribute")

    solr_docs = solr_return["response"]["docs"]

    # construct the response in the same format as postgres DB
    return_dict = {};
    return_dict["results"] = [];
    for doc in solr_docs:
        if "name" not in doc:
            continue

        return_dict["results"].append({
            0: doc["name"],
            1: "Element"
        })

    return jsonify(return_dict)

@app.route("/getMineralNames/<source>")
@cross_origin()
def get_mineral_names(source):
    solr_url = "http://localhost:8983/solr/docs/query?q=type:mineral AND source:" \
               + source + \
               "&rows=2147483647&wt=json"
    solr_return = requests.get(solr_url).json()

    # valid returned JSON
    if not "response" in solr_return:
        raise Exception("The returned list does not contain response attribute")

    if not "docs" in solr_return["response"]:
        raise Exception("Response attrbute does not contain docs sub-attribute")

    solr_docs = solr_return["response"]["docs"]

    # construct the response in the same format as postgres DB
    return_dict = {};
    return_dict["results"] = [];
    for doc in solr_docs:
        if "name" not in doc:
            continue

        return_dict["results"].append({
            0: doc["name"],
            1: "Mineral"
        })

    return jsonify(return_dict)

@app.route("/getPrimaryAuthorNames")
@cross_origin()
def get_primary_author_names():
    solr_url = "http://localhost:8983/solr/docs/query?q=type:doc&fl=primaryauthor&" \
               "rows=2147483647&wt=json"
    solr_return = requests.get(solr_url).json()

    # valid returned JSON
    if not "response" in solr_return:
        raise Exception("The returned list does not contain response attribute")

    if not "docs" in solr_return["response"]:
        raise Exception("Response attrbute does not contain docs sub-attribute")

    solr_docs = solr_return["response"]["docs"]

    # construct the response in the same format as postgres DB
    return_dict = {};
    return_dict["primary_author"] = [];
    for doc in solr_docs:
        if "primaryauthor" not in doc:
            continue

        return_dict["primary_author"].append({
            0: doc["primaryauthor"],
        })

    return jsonify(return_dict)

@app.route("/getStatistics/<source>")
@cross_origin()
def get_statistics(source):
    statistics = {}
    solr_doc_url = "http://localhost:8983/solr/docs/query?" \
                   "rows=0&q=_depth:0&facet=true&facet.field=type" \
                   "&facet.mincount=1&rows=2147483647&wt=json"
    solr_doc_return = requests.get(solr_doc_url).json()
    if not "facet_counts" in solr_doc_return:
        raise Exception("The returned list does not contain facet_counts field")
    if not "facet_fields" in solr_doc_return["facet_counts"]:
        raise Exception("facet_counts field does not contain facet_fields sub-attribtue");
    if not "type" in solr_doc_return["facet_counts"]["facet_fields"]:
        raise Exception("facet_fields doesn not contain type sub-attribute")
    solr_docs = solr_doc_return["facet_counts"]["facet_fields"]["type"]

    solr_other_url = "http://localhost:8983/solr/docs/query?rows=0&q=_depth:1&source:" \
                     + source + \
                     "&facet=true&facet.field=type&facet.mincount=1" \
                     "&rows=2147483647&wt=json"
    solr_other_return = requests.get(solr_other_url).json()
    if not "facet_counts" in solr_other_return:
        raise Expcetion("The returned list does not contain facet_counts field")
    if not "facet_fields" in solr_other_return["facet_counts"]:
        raise Exception("facet_counts field does not contain facet_fields sub attribute")
    if not "type" in solr_other_return["facet_counts"]["facet_fields"]:
        raise Exception("facet_fields field does not contain type sub attribute")
    solr_other = solr_other_return["facet_counts"]["facet_fields"]["type"]

    #iterate solr_docs to get the total counts of documents
    for idx, val in enumerate(solr_docs):
        if val == "doc":
            statistics["document_count"] = {
                0: {0: solr_docs[idx + 1]}
            }  #make it consitent with postgres adapter
            break

    #iterate solr_other to get the total counts of targets, contains, elements, features,
    #material, and minerals
    for idx, val in enumerate(solr_other):
        if val == "target":
            statistics["target_count"] = {
                0: {0: solr_other[idx + 1]}
            }  #make it consitent with postgres adapter
            continue

        if val == "contains":
            statistics["event_count"] =  {
                0: {0: solr_other[idx + 1]}
            }  #make it consitent with postgres adapter
            continue

        if val == "element":
            statistics["element_count"] = {
                0: {0: solr_other[idx + 1]}
            }  #make it consitent with postgres adapter
            continue

        if val == "feature":
            statistics["feature_count"] =  {
                0: {0: solr_other[idx + 1]}
            }  #make it consitent with postgres adapter
            continue

        if val == "material":
            statistics["material_count"] =  {
                0: {0: solr_other[idx + 1]}
            }  #make it consitent with postgres adapter
            continue

        if val == "mineral":
            statistics["mineral_count"] =  {
                0: {0: solr_other[idx + 1]}
            }  #make it consitent with postgres adapter
            continue

    return jsonify(statistics)

@app.route("/getResultsBySearchStr/<source>/<searchStr>")
@cross_origin()
def get_results_by_searchStr(source, searchStr):
    #store target names searched by searchStr.
    #searchStr can be:
    # 1. target name
    # 2. componment name (element name or mineral name)
    # 3. primary author name
    target_names = [];
    #store the search results that are returned to web
    #note that return_dict needs to be consistent with postgres DB
    results = []
    return_dict = {}

    #searchStr = target name case
    #target_names_tios
    # solr_target = "http://localhost:8983/solr/docs/query?q=target_names_ss:" \
    #               + searchStr + \
    #               "&fq=source:" \
    #               + source + \
    #               "&facet=true&facet.field=target_names_ss&rows=0&facet.mincount=1" \
    #               "&facet.limit=2147483647&wt=json"
    solr_target = "http://localhost:8983/solr/docs/query?q=target_names_tios:" \
                  + searchStr + \
                  "&fq=source:" \
                  + source + \
                  "&facet=true&facet.field=target_names_ss&rows=0&facet.mincount=1" \
                  "&facet.limit=2147483647&wt=json"
    solr_return = requests.get(solr_target).json()
    # valid returned JSON
    if not "facet_counts" in solr_return:
        raise Exception("The returned list does not contain facet_counts attribute")
    if not "facet_fields" in solr_return["facet_counts"]:
        raise Exception("facet_counts attrbute does not contain facet_fields sub-attribute")
    if not "target_names_ss" in solr_return["facet_counts"]["facet_fields"]:
        raise Exception("facet_fields attrbute does not contain target_names_ss sub-attribute")
    #Targets returned sometimes is a list. E.g. ["windjana", "stephen"] is retrieved when search
    # windjana, but we only need windjana. We process the returned list from ["windjana", "stephen"]
    # into just ["windjana"]. We get a list of targets when we search by target name, and then we
    # do a string match to remove un-needed targets.
    solr_target_names = solr_return["facet_counts"]["facet_fields"]["target_names_ss"]
    #step 1: remove integer counts first
    solr_target_names_no_integer = [target for target in solr_target_names if not isinstance(target, int)]
    #step 2: string match to remove un-needed targets
    solr_target_names_remove = [target for target in solr_target_names_no_integer
                                if searchStr.lower() == target.lower()]
    target_names.extend(solr_target_names_remove)
    print target_names

    #searchStr = conponment name case
    #Get target names by searching conponent name
    solr_target_by_component = "http://localhost:8983/solr/docs/query?q=cont_names_tios:"\
                               + searchStr + \
                               "&fq=source:" \
                               + source + \
                               "&facet=true&facet.field=target_names_ss&rows=0&facet.mincount=1" \
                               "&facet.limit=2147483647&wt=json"
    solr_return = requests.get(solr_target_by_component).json()
    # valid returned JSON
    if not "facet_counts" in solr_return:
        raise Exception("The returned list does not contain facet_counts attribute")
    if not "facet_fields" in solr_return["facet_counts"]:
        raise Exception("facet_counts attrbute does not contain facet_fields sub-attribute")
    if not "target_names_ss" in solr_return["facet_counts"]["facet_fields"]:
        raise Exception("facet_fields attrbute does not contain target_names_ss sub-attribute")
    #Targets name in ["windjana", 3, "big sky", 2, ...] format
    #Process it into ["windjana", "big sky", ...] format
    solr_target_names = solr_return["facet_counts"]["facet_fields"]["target_names_ss"]
    #rempve integer counts
    solr_target_names_no_integer = [target for target in solr_target_names if not isinstance(target, int)]
    target_names.extend(solr_target_names_no_integer)

    #searchStr = primary author name case
    solr_target_by_primaryauthor = "http://localhost:8983/solr/docs/query?q={!join+from=id+to=p_id}primaryauthor:" \
                                   + searchStr + \
                                   "&fq=source:" \
                                   + source + \
                                   " AND type:target&facet=true&facet.field=name&rows=0&facet.mincount=1" \
                                   "&facet.limit=2147483647&wt=json"
    solr_return = requests.get(solr_target_by_primaryauthor).json()
    # valid returned JSON
    if not "facet_counts" in solr_return:
        raise Exception("The returned list does not contain facet_counts attribute")
    if not "facet_fields" in solr_return["facet_counts"]:
        raise Exception("facet_counts attrbute does not contain facet_fields sub-attribute")
    if not "name" in solr_return["facet_counts"]["facet_fields"]:
        raise Exception("facet_fields attrbute does not contain name sub-attribute")
    # Targets name in ["windjana", 3, "big sky", 2, ...] format
    # Process it into ["windjana", "big sky", ...] format
    solr_target_names = solr_return["facet_counts"]["facet_fields"]["name"]
    # rempve integer counts
    solr_target_names_no_integer = [target for target in solr_target_names if not isinstance(target, int)]
    target_names.extend(solr_target_names_no_integer)

    for target_name in target_names:
        solr_contains = "http://localhost:8983/solr/docs/query?q={!join%20from=cont_ids_ss to=id}target_names_tios:" \
                        + target_name + \
                        "&rows=2147483647&wt=json"
        solr_return = requests.get(solr_contains).json()
        if not "response" in solr_return:
            raise Exception("The returned list does not contain response attribute")
        if not "docs" in solr_return["response"]:
            raise Exception("response attribute does not contain docs sub-attribute")
        solr_docs = solr_return["response"]["docs"]
        for doc in solr_docs:
            if not "p_id" in doc:
                break     #it really should raise an exception here
            if not "name" in doc:
                doc["name"] = "Undefined"
            if not "excerpt" in doc:
                doc["excerpt"] = "Undefined"
            if not "type" in doc:
                doc["type"] = "Undefined"

            solr_documents = "http://localhost:8983/solr/docs/query?q=type:doc&fq=id:" \
                             + doc["p_id"] + \
                             "&fl=primaryauthor,title,year,venue,url&wt=json"
            solr_return_info = requests.get(solr_documents).json()
            if not "response" in solr_return_info:
                raise Exception("The returned list does not contain response attribute")
            if not "docs" in solr_return_info["response"]:
                raise Exception("response attribute does not contain docs sub-attribute")
            solr_docs_info = solr_return_info["response"]["docs"]
            for doc_info in solr_docs_info:
                if not "primaryauthor" in doc_info:
                    doc_info["primaryauthor"] = "Undefined"
                if not "title" in doc_info:
                    doc_info["title"] = "Undefined"
                if not "year" in doc_info:
                    doc_info["year"] = "Undefined"
                if not "venue" in doc_info:
                    doc_info["venue"] = "Undefined"
                if not "url" in doc_info:
                    doc_info["url"] = "Undefined"
                results.append([target_name, "", "", doc["name"], doc["type"], doc_info["primaryauthor"],
                                doc_info["title"], doc["excerpt"], doc_info["year"], doc_info["venue"],
                                doc_info["url"]])
    return_dict["results"] = results

    return jsonify(return_dict)