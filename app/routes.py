from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.board import Board
from app.models.card import Card
import os
from dotenv import load_dotenv
import requests
from slack_sdk.errors import SlackApiError

boards_bp = Blueprint("boards", __name__, url_prefix="/boards")
hello_world_bp = Blueprint("hello_world", __name__)


load_dotenv()

# Basic route to test if the server is running


@hello_world_bp.route("/hello-world", methods=["GET"])
def hello_world():
    my_beautiful_response_body = "Hello, World!"
    return my_beautiful_response_body

# method to post message to slack


def post_message_to_slack(text):
    SLACK_TOKEN = os.environ.get('SLACKBOT_TOKEN')
    slack_path = "https://slack.com/api/chat.postMessage"
    query_params = {
        'channel': 'C0286U213J5',
        'text': text
    }
    headers = {'Authorization': f"Bearer {SLACK_TOKEN}"}
    requests.post(slack_path, params=query_params, headers=headers)

# routes for getting all boards and creating a new board


@boards_bp.route("", methods=["GET", "POST"])
def handle_boards():
    if request.method == "GET":
        boards = Board.query.all()
        boards_response = []
        for board in boards:
            boards_response.append({
                "board_id": board.board_id,
                "title": board.title,
                "owner": board.owner,
            })
        return jsonify(boards_response)
    elif request.method == "POST":
        request_body = request.get_json()
        title = request_body.get("title")
        owner = request_body.get("owner")
        new_board = Board(title=request_body["title"],
                          owner=request_body["owner"])
        db.session.add(new_board)
        db.session.commit()
        slack_message = f"Some duck just added a new board!"
        post_message_to_slack(slack_message)

    return make_response(f"Board {new_board.title} successfully created", 201)

# routes for getting a specific board, updating a board, and deleting a board


@boards_bp.route("/<board_id>", methods=["GET", "PUT", "DELETE"])
def handle_board(board_id):
    board = Board.query.get_or_404(board_id)
    if request.method == "GET":
        cards = []
        for card in board.cards:
            single_card = {
                "message": card.message,
            }
            cards.append(single_card)
        return make_response({
            "id": board.board_id,
            "title": board.title,
            "owner": board.owner,
            "cards": cards
        })
    elif request.method == "PUT":
        if board == None:
            return make_response("Board does not exist", 404)
        form_data = request.get_json()

        board.title = form_data["title"]
        board.owner = form_data["owner"]

        db.session.commit()

        return make_response(f"Board: {board.title} sucessfully updated.")

    elif request.method == "DELETE":
        if board == None:
            return make_response("Board does not exist", 404)
        db.session.delete(board)
        db.session.commit()
        return make_response(f"Board: {board.title} sucessfully deleted.")
# example_bp = Blueprint('example_bp', __name__)

# route for getting all cards in a board and making a new card


@boards_bp.route("/<board_id>/cards", methods=["POST", "GET"])
def handle_cards(board_id):
    board = Board.query.get(board_id)

    if board is None:
        return make_response("", 404)

    if request.method == "GET":
        cards = Board.query.get(board_id).cards
        cards_response = []
        for card in cards:
            cards_response.append({
                "message": card.message,
                "likes_count": card.likes_count,
            })

        return make_response(
            {
                "cards": cards_response
            }, 200)
    elif request.method == "POST":
        request_body = request.get_json()
        if 'message' not in request_body:
            return {"details": "Invalid data"}, 400

        new_card = Card(message=request_body["message"],
                        board_id=board_id)

        db.session.add(new_card)
        db.session.commit()
        slack_message = f"Some duck just added a new card!"
        post_message_to_slack(slack_message)

        return {
            "card": {
                "id": new_card.card_id,
                "message": new_card.message,
                "likes_count": new_card.likes_count,
            }
        }, 201

# route for deleting a card


@boards_bp.route("/<board_id>/<card_id>", methods=["DELETE"])
def handle_card(board_id, card_id):
    card = Card.query.get_or_404(card_id)

    db.session.delete(card)
    db.session.commit()

    return make_response(
        f"Card Message: {card.message} Card ID: {card.card_id} deleted successfully")
