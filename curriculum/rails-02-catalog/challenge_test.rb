# frozen_string_literal: false
require 'minitest/autorun'
require 'active_record'
ActiveRecord::Base.establish_connection(adapter:'sqlite3',database:':memory:')
ActiveRecord::Schema.verbose=false
ActiveRecord::Schema.define do
  create_table(:books) { |t| t.string :title; t.integer :price_cents; t.integer :stock; t.boolean :published }
end
require_relative 'app/models/book'
class CatalogTest < Minitest::Test
  def setup
    Book.delete_all
    @cheap=Book.create!(title:'Cheap',price_cents:100,stock:2,published:true)
    @mid=Book.create!(title:'Middle',price_cents:200,stock:1,published:true)
    @tie=Book.create!(title:'Tie',price_cents:200,stock:3,published:true)
    @hidden=Book.create!(title:'Hidden',price_cents:150,stock:3,published:false)
    @empty=Book.create!(title:'Empty',price_cents:120,stock:0,published:true)
    Book.create!(title:'Negative',price_cents:110,stock:-1,published:true)
  end
  def test_available_order_and_filter
    result=Book.available; assert_kind_of ActiveRecord::Relation,result; assert_equal([@cheap.id,@mid.id,@tie.id],result.pluck(:id))
  end
  def test_inclusive_price_bounds
    result=Book.priced_between(150,200); assert_kind_of ActiveRecord::Relation,result;assert_equal([@mid.id,@tie.id,@hidden.id].sort,result.pluck(:id).sort);assert_equal([@mid.id,@tie.id].sort,Book.priced_between(200,200).pluck(:id).sort)
  end
  def test_composable_relations
    assert_equal([@tie.id],Book.where(title:'Tie').available.priced_between(200,300).pluck(:id));assert_equal([@mid.id,@tie.id],Book.priced_between(150,300).available.pluck(:id));assert_equal([@cheap.id],Book.available.where(title:'Cheap').pluck(:id))
  end
  def test_invalid_bounds
    [[-1,2],[3,2],['1',2],[1,2.5],[nil,3]].each { |a,b| assert_raises(ArgumentError) { Book.priced_between(a,b) } }
  end
  def test_empty_relation_and_no_writes
    before=Book.order(:id).map(&:attributes);result=Book.available.priced_between(999,1000);assert_kind_of ActiveRecord::Relation,result;assert_equal(0,result.count);assert_equal([],result.pluck(:id));assert_equal(before,Book.order(:id).map(&:attributes))
  end
end
