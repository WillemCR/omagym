# frozen_string_literal: false
require 'minitest/autorun'
require 'json'
require 'action_controller'
require 'rack/mock'
require_relative 'app/controllers/shipping_quotes_controller'
class QuotesTest < Minitest::Test
  def request(body)
    env=Rack::MockRequest.env_for('/quotes',method:'POST',input:JSON.generate(body),'CONTENT_TYPE'=>'application/json')
    status,headers,response=ShippingQuotesController.action(:create).call(env)
    text='';response.each { |part| text << part };response.close if response.respond_to?(:close)
    assert_match(/application\/json/,headers['content-type']);[status,JSON.parse(text)]
  end
  def test_local_quote
    assert_equal([200,{'cents'=>400,'currency'=>'EUR'}],request({quote:{weight_grams:1,zone:'local'}}))
  end
  def test_weight_rounding_and_zones
    [[1000,'local',400],[1001,'local',500],[20000,'international',2900]].each { |weight,zone,cents| assert_equal([200,{'cents'=>cents,'currency'=>'EUR'}],request({quote:{weight_grams:weight,zone:zone}})) }
  end
  def test_missing_quote_object
    [{},{quote:nil},{quote:'bad'},{quote:[]}].each { |body| assert_equal([400,{'error'=>'quote_required'}],request(body)) }
  end
  def test_invalid_weight
    [nil,0,-1,20001,1.5,'1000',true].each { |weight| assert_equal([422,{'error'=>'invalid_quote'}],request({quote:{weight_grams:weight,zone:'local'}})) }
  end
  def test_invalid_zone
    [nil,'LOCAL','elsewhere',1].each { |zone| assert_equal([422,{'error'=>'invalid_quote'}],request({quote:{weight_grams:100,zone:zone}})) };assert_equal([422,{'error'=>'invalid_quote'}],request({quote:{}}))
  end
  def test_extra_fields_ignored
    assert_equal([200,{'cents'=>400,'currency'=>'EUR'}],request({quote:{weight_grams:100,zone:'local',cents:0,currency:'USD',admin:true},weight_grams:99999}))
  end
end
