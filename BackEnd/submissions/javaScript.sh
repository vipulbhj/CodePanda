cd submissions
javac $1
rc=$?
if [ $rc -eq 0 ]
then
	java $2 > result.txt
else
	echo "Error Occured while compiling the code.The code has errors" > result.txt
fi
cd ..
