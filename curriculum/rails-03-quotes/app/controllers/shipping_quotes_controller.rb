require 'action_controller'
class ShippingQuotesController < ActionController::API
  def create
    render json: { error: 'not_implemented' }, status: :not_implemented
  end
end
