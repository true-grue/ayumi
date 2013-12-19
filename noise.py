for i in range(32):
  for j in range(60):
    print "0 0 0 0 0 0 %d 4 15 0 0 0 0 255 0 0" % (i)
  for j in range(4):
    print "0 0 0 0 0 0 0 0 0 0 0 0 0 255 0 0"

for j in range(60):
  print "0 0 0 0 0 0 %d 4 15 0 0 0 0 255 0 0" % 0
for j in range(4):
  print "0 0 0 0 0 0 0 0 0 0 0 0 0 255 0 0"
