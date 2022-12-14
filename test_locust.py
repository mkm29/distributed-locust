from typing import Optional
from faker import Faker
import random
import requests

class FirecornUserTest:

    fake = Faker()

    @property
    def api_url(self):
        return "https://api-firecorn.apps.dev.agiledagger.io/"

    def _create_user(self) -> Optional[int]:
        # Create a new user
        mutation = """
        mutation {
            createUser(userDetails: {
                name: "%s",
                sex: "%s",
                address: "%s",
                phoneNumber: "%s",
            })
            {
                id
            }
        }
        """ % (
            self.fake.name(),
            self.fake.random_element(elements=("male", "female")),
            "".join(self.fake.address().splitlines()),
            random.randint(0000000000,9999999999),
        )
        mutation = mutation.replace("/n","")
        print("Mutation: \n", mutation)
        response = requests.post(
            self.api_url,
            headers=self.headers,
            data={"query": mutation},
        )
        print("Response: ", response)
        data = response.json()
        if data["data"]["id"]:
            with open("/tmp/user_ids.txt", "a") as f:
                print("Added user with id: %d" % data["data"]["id"])
                f.write(data["data"]["id"] + "\n")
            return data["data"]["id"]
        else:
            print("Unable to create user")
            return None

    def on_start(self):
        """on_start is called when a Locust start before any task is scheduled"""
        # Create a few users by using the API
        for _ in range(3):
            self._create_user()

    @property
    def headers(self):
        return {"Accept": "application/graphql"}

    def get_random_id(self, type):
        if type not in ["user", "post", "comment"]:
            return None
        # open up shared file of user ids
        return random.choice(
            list(line.strip() for line in open(f"/tmp/{type}_ids.txt"))
        )

    def create_user(self):
        self._create_user()

    def query_users(self):
        query = """
        query {
            getUsers {
                name
                address
            }
        }
        """
        query = query.replace("/n","")
        _ = requests.post(
            self.api_url,
            headers=self.headers,
            data={"query": query},
        )

    def create_post(self):
        # This should a random user
        mutation = """
        mutation createPost {
        createPost(postDetails: {
            userId: %d,
            title: "%s",
            body: "%s"
        })
        {
            id
            body
        }
        }
        """ % (
            self.get_random_id(type="user"),
            self.fake.sentence(),
            self.fake.text(),
        )
        mutation = mutation.replace("/n","")
        response = requests.post(
            self.api_url,
            headers=self.headers,
            data={"query": mutation},
        )
        data = response.json()
        if data["data"]["id"]:
            with open("/tmp/post_ids.txt", "a") as f:
                print("Added post with id: %d" % data["data"]["id"])
                f.write(data["data"]["id"] + "\n")

    def get_posts(self):
        query = """
        query {
            getPosts {
                id
                body
            }
        }
        """
        query = query.replace("/n","")
        _ = requests.post(
            self.api_url,
            headers=self.headers,
            data={"query": query},
        )

    def create_comment(self):
        mutation = """
        mutation createComment {
            createComment(commentDetails: {
                userId: %d,
                postId: %d,
                body: "%s"
            })
            {
                id
                body
            }
        }
        """ % (
            self.get_random_id(type="user"),
            self.get_random_id(type="post"),
            self.fake.text(),
        )
        mutation = mutation.replace("/n","")
        response = requests.post(
            self.api_url,
            headers=self.headers,
            data={"query": mutation},
        )
        data = response.json()
        if data["data"]["id"]:
            with open("/tmp/comment_ids.txt", "a") as f:
                print("Added comment with id: %d" % data["data"]["id"])
                f.write(data["data"]["id"] + "\n")

    def get_comments(self):
        query = """
        query {
            getComments {
                id
                body
            }
        }
        """
        query = query.replace("/n","")
        _ = requests.post(
            self.api_url,
            headers=self.headers,
            data={"query": query},
        )

if __name__ == "__main__":
    client = FirecornUserTest()
    client.create_user()