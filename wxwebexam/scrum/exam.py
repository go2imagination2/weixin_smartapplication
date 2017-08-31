#!encoding=utf8
import unittest
import re


raw_text = u"""1、安全生产“三违”{违章指挥}、{违章操作}、 {违反劳动纪律}。

2、我国铁路的轨距为1520mm。(错)

3、从业人员有权（ A ）违章指挥和强令冒险作业。 [单选题]
A.拒绝
B.抵制
C.抗拒

4、安全教育的种类包括( ABCD)。 [多选题]
A.转岗教育
B.三级安全教育
C.特种作业人员安全教育
D.经常性安全教育"""

class Question(object):
	desc = ''
	right_answer = []
	options = []
	category = ''
	index_num = 0

	def __init__(self, raw):
		self.raw = raw
		lines = raw.split('\n')
		m = re.match(u'(\d+).*[（|(] (\w+)[ ）|)].*', lines[0])
		self.index_num = int(m.groups()[0])
		if lines[0].endswith(u'[单选题]'):
			self.category = 'Single Choice'
			self.options = lines[1:]
			self.right_answer = [m.groups()[1]]
		elif lines[0].endswith(u'[多选题]'):
			self.category = 'Multi Choice'
			self.options = lines[1:]
			self.right_answer = [m.groups()[1]]


class TestExam(unittest.TestCase):

    def test_parse_q2(self):
    	text = raw_text.split('\n\n')[2]
    	print text

        q2 = Question(text)
        self.assertEquals('Single Choice', q2.category)
        self.assertEquals(3, q2.index_num)
        self.assertEquals(['A'], q2.right_answer)
        self.assertEquals([u'A.拒绝', u'B.抵制', u'C.抗拒'], q2.options)

    def test_parse_q4(self):
    	text = raw_text.split('\n\n')[3]
    	print text

        q3 = Question(text)
        self.assertEquals('Multi Choice', q3.category)
        self.assertEquals(4, q3.index_num)
        self.assertEquals(['ABCD'], q3.right_answer)
        self.assertEquals([u'A.转岗教育', u'B.三级安全教育', u'C.特种作业人员安全教育', u'D.经常性安全教育'], q3.options)

if __name__ == '__main__':
    unittest.main()
