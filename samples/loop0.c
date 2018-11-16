main()
{
	int K = 1;
	while(K<3)
	{	
		int a = __VERIFIER_nondet_int();
		__VERIFIER_assume(a > 0);
		int i = 0;
		while(i < a)
		{
			i++;
		}
		
		K++;
		__VERIFIER_assume(!(i<a));
		//__VERIFIER_assume(!(K < 3));
		__VERIFIER_assert(i <= a);
	}
	
}
