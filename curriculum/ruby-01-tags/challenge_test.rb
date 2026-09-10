# frozen_string_literal: false
require 'minitest/autorun'
require_relative 'main'
class TagsTest < Minitest::Test
  def test_empty
    assert_equal({}, tag_index([]))
  end
  def test_normalization_and_deduplication
    assert_equal({'ruby'=>[2,9], 'web'=>[9]}, tag_index([{id:9,tags:[' Ruby ','ruby','Web',' ']},{id:2,tags:['RUBY']}]))
  end
  def test_unicode_and_punctuation
    assert_equal({'c++'=>[1], 'été'=>[1]}, tag_index([{id:1,tags:['C++','ÉTÉ']}]))
  end
  def test_immutable_input
    tags=[' Ruby '.freeze].freeze; article={id:1,tags:tags}.freeze; input=[article].freeze
    assert_equal({'ruby'=>[1]},tag_index(input)); assert_equal(' Ruby ',tags.first)
  end
  def test_invalid_records
    [nil,{},[nil],[{}],[{id:0,tags:[]}],[{id:'1',tags:[]}],[{id:1,tags:'ruby'}],[{id:1,tags:[nil]}],[{id:1,tags:[]},{id:1,tags:[]}]].each do |input|
      assert_raises(ArgumentError) { tag_index(input) }
    end
  end
end
