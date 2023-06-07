#!/bin/bash
echo $1 >> $2;
right=$(paste -d "" <(cat $1|cut -f 2|grep -o .) <(cat test.tsv|cut -f 2|grep -o .)|grep -E -e RR -e NN -e SS -e II -e PP|wc -l);
total=$(paste -d "" <(cat $1|cut -f 2|grep -o .) <(cat test.tsv|cut -f 2|grep -o .)|wc -l);
echo $right
echo $total
echo $(echo "scale=3;100 * $right/$total"|bc)
result=$(echo "100 * $right/$total"|bc);
echo $result >> $2;
paste -d ":" <(cat test.tsv|cut -f 2|grep -o .) <(cat $1|cut -f 2|grep -o .)|sort|uniq -c

