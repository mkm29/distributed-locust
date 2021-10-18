from locust import HttpUser, task, between
from faker import Faker

class FirecornUserTest(HttpUser):

    wait_time = between(0.5, 3.0)
    fake = Faker()

    @task(1)
    def create_user(self):
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
                name
                address
            }
        }
        """ % (
            self.fake.name(),
            self.fake.random_element(elements=("male", "female")),
            self.fake.address(),
            self.fake.phone_number(),
        )
        _ = self.client.post(
            "http://localhost:8080/",
            name="CreateUser",
            headers={
                "Accept": "application/graphql",
            },
            json={"query": mutation},
        )

    @task(2)
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
            "http://localhost:8080/",
            name="GetUsers",
            headers={
                "Accept": "application/graphql",
            },
            json={"query": query},
        )

    @task(3)
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
            self.fake.random_int(min=1, max=100),
            self.fake.sentence(),
            self.fake.text()
        )
        _ = self.client.post(
            "http://localhost:8080/",
            name="CreatePost",
            headers={
                "Accept": "application/graphql",
            },
            json={"query": mutation},
        )

    @task(2)
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
            "http://localhost:8080/",
            name="GetPosts",
            headers={
                "Accept": "application/graphql",
            },
            json={"query": query},
        )

    @task(5)
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
            self.fake.random_int(min=1, max=100),
            self.fake.random_int(min=1, max=100),
            self.fake.text()
        )
        _ = self.client.post(
            "http://localhost:8080/",
            name="CreateComment",
            headers={"Accept": "application/graphql",},
            json={"query": mutation}
        )

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
            "http://localhost:8080/",
            name="GetPosts",
            headers={
                "Accept": "application/graphql",
            },
            json={"query": query},
        )
