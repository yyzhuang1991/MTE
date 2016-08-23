# brat_annotation.py
# Helper methods for parsing and manipulating brat annotations.
# Strongly inspired by 
# https://github.com/ryanaustincarlson/moocdb/blob/master/annotate/BratAnnotation.py
#
# Kiri Wagstaff
# January 12, 2016

import sys, os
import dbutils


class BratAnnotation:
    def __init__(self, annotation_line, doc_id, username):
        self.doc_id   = doc_id
        self.username = username

        #annotation_id, markup, name = annotation_line.strip().split('\t')
        splitline = annotation_line.strip().split('\t')
        self.annotation_id = splitline[0]

        if splitline[0][0] == 'T': # target
            self.label   = splitline[1].split()[0]
            args         = splitline[1].split()[1:]
            self.start   = args[0]
            self.end     = args[-1]
            self.name    = splitline[2]
        elif splitline[0][0] == 'E': # event
            args         = splitline[1].split() 
            self.label   = args[0].split(':')[0]+'_event'
            self.anchor  = args[0].split(':')[1]
            args         = [a.split(':') for a in args[1:]]
            self.targets = [v for (t,v) in args if t == 'Targ']
            self.cont    = [v for (t,v) in args if t == 'Cont']
        elif splitline[0][0] == 'R': # relation
            label, arg1, arg2 = splitline[1].split() # assumes 2 args
            self.label   = label
            self.arg1    = arg1.split(':')[1]
            self.arg2    = arg2.split(':')[1]
        elif splitline[0][0] == 'A': # attribute
            label, arg, value = splitline[1].split()
            self.label   = label
            self.arg1    = arg
            self.value   = value
        else:
            print 'Unknown annotation type:', splitline[0]


    def insert(self, cursor):

        # Insert into the appropriate table depending on the annotation type

        if (self.label == 'Target' or 
            self.label == 'Contains' or
            self.label == 'DoesNotContain' or
            self.label == 'StratRel'): 
            # If it's just 'Contains' or 'DoesNotContain' with no arguments,
            # it is the anchor for an 'event', so add it
            # to the targets table for later reference (to get excerpts).
            dbutils.insert_into_table(
                cursor=cursor,
                table='targets',
                columns=['target_id', 'target_name', 'span_start', 'span_end'],
                values=[self.doc_id+'_'+self.annotation_id, 
                        self.name,
                        self.start,
                        self.end])
        elif (self.label == 'Element' or 
              self.label == 'Mineral' or 
              self.label == 'Material' or 
              self.label == 'Feature'):
            dbutils.insert_into_table(
                cursor=cursor,
                table='components',
                columns=['component_id', 'component_name', 'component_label',
                         'span_start', 'span_end'],
                values=[self.doc_id+'_'+self.annotation_id, 
                        self.name, 
                        self.label,
                        self.start,
                        self.end])
        elif self.label == 'Contains_event':
            # Loop over all targets
            for t in self.targets:
                # Loop over all constituents
                for v in self.cont:
                    # Extract the excerpt 
                    cursor.execute("SELECT content " +
                                   "FROM documents " +
                                   "WHERE doc_id='%s';" \
                                       % (self.doc_id))
                    content = cursor.fetchone()
                    if content == None:
                        print 'Warning: document %s not found, skipping.' % \
                            self.doc_id
                        break

                    content = content[0]
                    cursor.execute("SELECT span_start, span_end " +
                                   "FROM targets " +
                                   "WHERE target_id='%s';" \
                                       % (self.doc_id+'_'+self.anchor))
                    (anchor_start,anchor_end) = cursor.fetchone()
                    sent_start = max(content[:anchor_start].rfind('.'),0)+1
                    sent_end   = anchor_end + \
                        min(content[anchor_end:].find('.'),len(content))+1
                    excerpt = content[sent_start:sent_end]

                    # Insert into table
                    dbutils.insert_into_table(
                        cursor=cursor,
                        table='contains',
                        columns=['event_id',  'doc_id', 
                                 'target_id', 'component_id', 
                                 'magnitude', 'confidence',   
                                 'annotator', 'excerpt'],
                        values=[self.doc_id+'_'+self.annotation_id, 
                                self.doc_id,
                                self.doc_id+'_'+t,
                                self.doc_id+'_'+v,
                                'unknown',
                                'neutral',
                                self.username,
                                excerpt])
        elif (self.label == 'Amount' or
              self.label == 'Associated' or
              self.label == 'BelongsTo' or
              self.label == 'Confidence' or
              self.label == 'DoesNotContain_event' or
              self.label == 'DoesNotShow' or
              self.label == 'Formation' or 
              self.label == 'IsSituatedIn' or
              self.label == 'Locality' or
              self.label == 'Material' or
              self.label == 'Member' or
              self.label == 'Position' or 
              self.label == 'Process' or
              self.label == 'Region' or
              self.label == 'Shows' or
              self.label == 'Site' or
              self.label == 'StratRel_event' or
              self.label == 'Unit'):
            # Not yet handled
            pass
        else:
            raise RuntimeError('Unknown label %s' % self.label)

