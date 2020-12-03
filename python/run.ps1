if ( $args.count -gt 0 ) 
{   
    python code_generator.py $args[0]
} 
else 
{
    python code_generator.py
}
gcc -c .\final.s -o final.o
gcc final.o -o final.exe
./final.exe

