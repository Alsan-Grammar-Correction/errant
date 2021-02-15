import errant

annotator = errant.load('ar')
orig = annotator.parse('ذهبت الطالب إلى المدرسة')
#print('Type of orig is ', type(orig))

#for t in orig:
#  print(t, t.pos_, t.dep_)

cor = annotator.parse('ذهب الطالب إلى المدرسة')
#print('\nType of cor is ', type(cor))

#for t in cor:
#  print(t, t.pos_, t.dep_)

edits = annotator.annotate(orig, cor)
for e in edits:
    print(e.o_start, e.o_end, e.o_str, e.c_start, e.c_end, e.c_str, e.type)
