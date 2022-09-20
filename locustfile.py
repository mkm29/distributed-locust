from typing import Optional
from locust import TaskSet, task, HttpUser, between
import random
from faker import Faker
import logging

baseEndpoint = 'https://api-firecorn.apps.dev.agiledagger.io/'
headers = {"Accept": "application/graphql"}
fake = Faker()

def get_random_id(type):
    if type not in ["user", "post", "comment"]:
        return None
    # open up shared file of user ids
    return random.choice(
        list(line.strip() for line in open(f"/tmp/{type}_ids.txt"))
    ) 

class UserTasks(TaskSet):

    @task(2)
    def get_all_users(self):
        query = """
        query {
            getUsers {
                name
                address
            }
        }
        """
        query = query.replace("/n","")
        _ = self.client.post(
            baseEndpoint,
            name="GetUsers",
            headers=headers,
            json={"query": query},
        )

    @task(1)
    def create_user(self) -> Optional[int]:
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
            fake.name(),
            fake.random_element(elements=("male", "female")),
            " ".join(fake.address().splitlines()),
            random.randint(0000000000,9999999999),
        )
        mutation = mutation.replace("/n","")
        response = self.client.post(
            baseEndpoint,
            name="CreateUser",
            headers=headers,
            json={"query": mutation},
        )
        data = response.json()
        print(data)
        if data["data"]['createUser']["id"]:
            user_id = int(data["data"]['createUser']["id"])
            with open("/tmp/user_ids.txt", "a") as f:
                print("Added user with id: %d" % user_id)
                f.write(data["data"]['createUser']["id"] + "\n")
            return user_id
        else:
            print("Unable to create user")
            return None

class PostTasks(TaskSet):
    
        @task(2)
        def get_all_posts(self):
            query = """
            query {
                getPosts {
                    title
                    body
                }
            }
            """
            query = query.replace("/n","")
            _ = self.client.post(
                baseEndpoint,
                name="GetPosts",
                headers=headers,
                json={"query": query},
            )
    
        @task(1)
        def create_post(self) -> Optional[int]:
            # Create a new post
            post_id = get_random_id("post")
            if not post_id:
                return None
            mutation = """
            mutation {
                createPost(postDetails: {
                    title: "%s",
                    body: "%s",
                    userId: %d
                })
                {
                    id
                }
            }
            """ % (
                " ".join(fake.sentence().splitlines()),
                " ".join(fake.text().splitlines()),
                post_id,
            )
            mutation = mutation.replace("/n","")
            response = self.client.post(
                baseEndpoint,
                name="CreatePost",
                headers=headers,
                json={"query": mutation},
            )
            data = response.json()
            if data["data"]['createPost']["id"]:
                post_id = int(data["data"]['createPost']["id"])
                with open("/tmp/post_ids.txt", "a") as f:
                    print("Added post with id: %d" % post_id)
                    f.write(data["data"]['createPost']["id"] + "\n")
                return post_id


class ApiUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        logging.info("Begin Locust load/stress test")

    def on_stop(self) -> None:
        logging.info("End Locust load/stress test")

    tasks = {UserTasks, PostTasks}