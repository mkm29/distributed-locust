from locust import HttpUser, task, between
from faker import Faker
import random


class FirecornUserTest(HttpUser):

    wait_time = between(0.5, 3.0)
    fake = Faker()

    def _create_user(self) -> int:
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
            self.fake.address(),
            self.fake.phone_number(),
        )
        response = self.client.post(
            "https://api-firecorn.apps.dev.agiledagger.io/",
            name="CreateUser",
            headers=self.headers,
            json={"query": mutation},
        )
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
        for i in range(3):
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

    @task(3)
    def create_user(self):
        self._create_user()

    @task(5)
    def query_users(self):
        query = """
        query {
            getUsers {
                name
                address
            }
        }
        """
        _ = self.client.post(
            "https://api-firecorn.apps.dev.agiledagger.io/",
            name="GetUsers",
            headers=self.headers,
            json={"query": query},
        )

    @task(2)
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
        data = self.client.post(
            "https://api-firecorn.apps.dev.agiledagger.io/",
            name="CreatePost",
            headers=self.headers,
            json={"query": mutation},
        )
        data = response.json()
        if data["data"]["id"]:
            with open("/tmp/post_ids.txt", "a") as f:
                print("Added post with id: %d" % data["data"]["id"])
                f.write(data["data"]["id"] + "\n")

    @task(4)
    def get_posts(self):
        query = """
        query {
            getPosts {
                id
                body
            }
        }
        """
        _ = self.client.post(
            "https://api-firecorn.apps.dev.agiledagger.io/",
            name="GetPosts",
            headers=self.headers,
            json={"query": query},
        )

    @task(1)
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
        data = self.client.post(
            "https://api-firecorn.apps.dev.agiledagger.io/",
            name="CreateComment",
            headers=self.headers,
            json={"query": mutation},
        )
        data = response.json()
        if data["data"]["id"]:
            with open("/tmp/comment_ids.txt", "a") as f:
                print("Added comment with id: %d" % data["data"]["id"])
                f.write(data["data"]["id"] + "\n")

    @task(2)
    def get_comments(self):
        query = """
        query {
            getComments {
                id
                body
            }
        }
        """
        _ = self.client.post(
            "https://api-firecorn.apps.dev.agiledagger.io/",
            name="GetPosts",
            headers=self.headers,
            json={"query": query},
        )
