
#function to remove punctuations, spaces from string and make it lowercase.
def strip_str(text):		
	punctuations = ''' !-;:`'".,/_?'''
	text2 = ""
	for char in text.lower():
		if char not in punctuations:
			text2 = text2 + char
	return text2