cd submissions
gcc $1
rc=$?
if [ $rc -eq 0 ]
then
	./a.out > result.txt
else
	echo "Error Occured while compiling the code.The code has errors" > result.txt
fi
cd ..
