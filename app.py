import streamlit as st
from database import connect_db

st.set_page_config(
    page_title="Student Skill Sharing Platform",
    page_icon="🎓",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "searched" not in st.session_state:
    st.session_state["searched"] = False

if "students" not in st.session_state:
    st.session_state["students"] = []


# ==================================================
# LOGIN / REGISTRATION
# ==================================================

if not st.session_state["logged_in"]:

    register_tab, login_tab = st.tabs(["👤 Register", "🔐 Login"])

    with register_tab:
        st.header("👤 Student Registration")

        name = st.text_input("Enter your name", key="register_name")
        email = st.text_input("Enter your email", key="register_email")
        password = st.text_input(
            "Create a password",
            type="password",
            key="register_password"
        )

        if st.button("Register", key="register_button"):
            if name == "" or email == "" or password == "":
                st.warning("Please fill in all the fields.")
            else:
                try:
                    connection = connect_db()
                    cursor = connection.cursor()

                    cursor.execute(
                        """
                        INSERT INTO users (name, email, password)
                        VALUES (?, ?, ?)
                        """,
                        (name, email, password)
                    )

                    connection.commit()
                    connection.close()

                    st.success("Registration successful! 🎉")

                except Exception:
                    st.error("This email is already registered.")

    with login_tab:
        st.header("🔐 Student Login")

        login_email = st.text_input(
            "Enter your email",
            key="login_email"
        )

        login_password = st.text_input(
            "Enter your password",
            type="password",
            key="login_password"
        )

        if st.button("Login", key="login_button"):
            if login_email == "" or login_password == "":
                st.warning("Please enter your email and password.")
            else:
                connection = connect_db()
                cursor = connection.cursor()

                cursor.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE email = ?
                    AND password = ?
                    """,
                    (login_email, login_password)
                )

                user = cursor.fetchone()
                connection.close()

                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user[0]
                    st.session_state["user_name"] = user[1]
                    st.session_state["user_email"] = user[2]

                    st.rerun()
                else:
                    st.error("Invalid email or password.")


# ==================================================
# LOGGED-IN STUDENT
# ==================================================

else:

    st.sidebar.success(
        f"Logged in as {st.session_state['user_name']}"
    )

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["searched"] = False
        st.session_state["students"] = []
        st.rerun()


    # ==================================================
    # STUDENT PROFILE
    # ==================================================

    st.header("👤 Student Profile")

    st.subheader(
        f"Welcome, {st.session_state['user_name']}! 🎉"
    )

    st.write(
        f"📧 **Email:** {st.session_state['user_email']}"
    )

    st.divider()


    # ==================================================
    # ADD SKILL
    # ==================================================

    st.subheader("🛠️ Add Your Skill")

    skill_name = st.text_input(
        "Enter a skill",
        placeholder="Example: Python",
        key="skill_name"
    )

    skill_type = st.selectbox(
        "Skill Type",
        ["I Can Teach", "I Want to Learn"],
        key="skill_type"
    )

    if st.button("Add Skill", key="add_skill_button"):
        if skill_name == "":
            st.warning("Please enter a skill.")
        else:
            connection = connect_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO skills (user_id, skill_name, skill_type)
                VALUES (?, ?, ?)
                """,
                (
                    st.session_state["user_id"],
                    skill_name,
                    skill_type
                )
            )

            connection.commit()
            connection.close()

            st.success("Skill added successfully! 🎉")


    # ==================================================
    # MY SKILLS
    # ==================================================

    st.divider()
    st.subheader("📋 My Skills")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT skill_name, skill_type
        FROM skills
        WHERE user_id = ?
        """,
        (st.session_state["user_id"],)
    )

    skills = cursor.fetchall()
    connection.close()

    if skills:
        for skill in skills:
            if skill[1] == "I Can Teach":
                st.write(
                    f"🟢 **{skill[0]}** — I Can Teach"
                )
            else:
                st.write(
                    f"🔵 **{skill[0]}** — I Want to Learn"
                )
    else:
        st.info("You haven't added any skills yet.")


    # ==================================================
    # SEARCH STUDENTS
    # ==================================================

    st.divider()
    st.header("🔍 Find Students by Skill")

    st.write(
        "Search for a skill you want to learn "
        "and find students who can teach it."
    )

    search_skill = st.text_input(
        "Enter the skill you want to learn",
        placeholder="Example: Python",
        key="search_skill"
    )

    if st.button("🔍 Search Students", key="search_button"):
        if search_skill == "":
            st.warning("Please enter a skill to search.")
        else:
            connection = connect_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    users.id,
                    users.name,
                    users.email,
                    skills.skill_name
                FROM users
                JOIN skills
                    ON users.id = skills.user_id
                WHERE skills.skill_name LIKE ?
                AND skills.skill_type = 'I Can Teach'
                AND users.id != ?
                """,
                (
                    "%" + search_skill + "%",
                    st.session_state["user_id"]
                )
            )

            students = cursor.fetchall()
            connection.close()

            st.session_state["students"] = students
            st.session_state["searched"] = True


    # ==================================================
    # DISPLAY SEARCH RESULTS
    # ==================================================

    if st.session_state["searched"]:

        students = st.session_state["students"]

        if students:
            st.success(
                f"Found {len(students)} student(s)! 🎉"
            )

            for student in students:
                st.subheader(f"👤 {student[1]}")

                st.write(f"📧 Email: {student[2]}")
                st.write(f"🛠️ Skill: {student[3]}")

                if st.button(
                    f"🤝 Send Request to {student[1]}",
                    key=f"request_{student[0]}_{student[3]}"
                ):
                    connection = connect_db()
                    cursor = connection.cursor()

                    cursor.execute(
                        """
                        SELECT id
                        FROM requests
                        WHERE sender_id = ?
                        AND receiver_id = ?
                        AND skill = ?
                        """,
                        (
                            st.session_state["user_id"],
                            student[0],
                            student[3]
                        )
                    )

                    existing_request = cursor.fetchone()

                    if existing_request:
                        st.warning(
                            "You have already sent a request for this skill."
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO requests
                            (sender_id, receiver_id, skill, status)
                            VALUES (?, ?, ?, 'Pending')
                            """,
                            (
                                st.session_state["user_id"],
                                student[0],
                                student[3]
                            )
                        )

                        connection.commit()

                        st.success(
                            f"Request sent to {student[1]}! 🤝"
                        )

                    connection.close()

                st.divider()
        else:
            st.info("No students found with this skill.")


    # ==================================================
    # REQUESTS RECEIVED
    # ==================================================

    st.header("📨 Skill Sharing Requests")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            requests.id,
            users.name,
            users.email,
            requests.skill,
            requests.status
        FROM requests
        JOIN users
            ON requests.sender_id = users.id
        WHERE requests.receiver_id = ?
        ORDER BY requests.id DESC
        """,
        (st.session_state["user_id"],)
    )

    received_requests = cursor.fetchall()
    connection.close()

    if received_requests:

        for request in received_requests:
            request_id = request[0]
            sender_name = request[1]
            sender_email = request[2]
            skill = request[3]
            status = request[4]

            st.subheader(f"👤 {sender_name}")
            st.write(f"📧 Email: {sender_email}")
            st.write(f"🛠️ Wants to learn: **{skill}**")
            st.write(f"📌 Status: **{status}**")

            if status == "Pending":

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "✅ Accept",
                        key=f"accept_{request_id}"
                    ):
                        connection = connect_db()
                        cursor = connection.cursor()

                        cursor.execute(
                            """
                            UPDATE requests
                            SET status = 'Accepted'
                            WHERE id = ?
                            """,
                            (request_id,)
                        )

                        connection.commit()
                        connection.close()

                        st.success("Request accepted! 🤝")
                        st.rerun()

                with col2:
                    if st.button(
                        "❌ Reject",
                        key=f"reject_{request_id}"
                    ):
                        connection = connect_db()
                        cursor = connection.cursor()

                        cursor.execute(
                            """
                            UPDATE requests
                            SET status = 'Rejected'
                            WHERE id = ?
                            """,
                            (request_id,)
                        )

                        connection.commit()
                        connection.close()

                        st.warning("Request rejected.")
                        st.rerun()

            st.divider()

    else:
        st.info(
            "You don't have any skill-sharing requests yet."
        )


    # ==================================================
    # LEARNING RESOURCES
    # ==================================================

    st.header("📚 Learning Resources")

    st.write(
        "Share useful notes, tutorials, courses, "
        "and learning websites with other students."
    )

    st.subheader("➕ Share a Learning Resource")

    resource_title = st.text_input(
        "Resource Title",
        placeholder="Example: Python Programming Tutorial",
        key="resource_title"
    )

    resource_link = st.text_input(
        "Resource Link",
        placeholder="Example: https://www.python.org/",
        key="resource_link"
    )

    resource_description = st.text_area(
        "Description",
        placeholder="Write a short description of this resource",
        key="resource_description"
    )

    if st.button(
        "📤 Share Resource",
        key="share_resource_button"
    ):

        if resource_title == "" or resource_link == "":
            st.warning(
                "Please enter the resource title and link."
            )
        else:
            connection = connect_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO resources
                (user_id, title, link, description)
                VALUES (?, ?, ?, ?)
                """,
                (
                    st.session_state["user_id"],
                    resource_title,
                    resource_link,
                    resource_description
                )
            )

            connection.commit()
            connection.close()

            st.success(
                "Learning resource shared successfully! 📚🎉"
            )

            st.rerun()


    # ==================================================
    # VIEW SHARED RESOURCES
    # ==================================================

    st.divider()
    st.subheader("📖 Shared Resources")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            resources.title,
            resources.link,
            resources.description,
            users.name
        FROM resources
        JOIN users
            ON resources.user_id = users.id
        ORDER BY resources.id DESC
        """
    )

    resources = cursor.fetchall()
    connection.close()

    if resources:

        for resource in resources:
            title = resource[0]
            link = resource[1]
            description = resource[2]
            shared_by = resource[3]

            st.markdown(f"### 📚 {title}")
            st.write(f"👤 **Shared by:** {shared_by}")

            if description:
                st.write(
                    f"📝 **Description:** {description}"
                )

            st.markdown(
                f"🔗 [Open Resource]({link})"
            )

            st.divider()

    else:
        st.info(
            "No learning resources have been shared yet."
        )


    # ==================================================
    # RATINGS AND REVIEWS
    # ==================================================

    if "review_submitted" not in st.session_state:
        st.session_state["review_submitted"] = False

    if st.session_state["review_submitted"]:
        st.success("Rating and review submitted successfully! ⭐")
        st.session_state["review_submitted"] = False

    st.header("⭐ Student Ratings & Reviews")

    st.write(
        "Rate students after an accepted skill-sharing request."
    )

    st.subheader("⭐ Give a Rating")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT
            users.id,
            users.name
        FROM users
        JOIN requests
            ON users.id = requests.receiver_id
        WHERE requests.sender_id = ?
        AND requests.status = 'Accepted'
        AND users.id != ?
        """,
        (
            st.session_state["user_id"],
            st.session_state["user_id"]
        )
    )

    students_to_review = cursor.fetchall()
    connection.close()

    if students_to_review:

        student_options = {}

        for student in students_to_review:
            student_options[student[1]] = student[0]

        selected_student = st.selectbox(
            "Select a student to review",
            list(student_options.keys()),
            key="selected_student"
        )

        rating = st.slider(
            "Rating",
            min_value=1,
            max_value=5,
            value=5,
            step=1,
            key="rating"
        )

        review_text = st.text_area(
            "Write your review",
            placeholder="Write something about your learning experience...",
            key="review_text"
        )

        if st.button(
            "⭐ Submit Review",
            key="submit_review_button"
        ):

            reviewed_id = student_options[selected_student]

            connection = connect_db()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO reviews
                (reviewer_id, reviewed_id, rating, review)
                VALUES (?, ?, ?, ?)
                """,
                (
                    st.session_state["user_id"],
                    reviewed_id,
                    rating,
                    review_text
                )
            )

            connection.commit()
            connection.close()

            st.session_state["review_submitted"] = True
            st.rerun()

    else:
        st.info(
            "You can review students after an accepted skill-sharing request."
        )


    # ==================================================
    # DISPLAY REVIEWS
    # ==================================================

    st.divider()
    st.subheader("💬 Student Reviews")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            users.name,
            reviews.rating,
            reviews.review
        FROM reviews
        JOIN users
            ON reviews.reviewer_id = users.id
        WHERE reviews.reviewed_id = ?
        ORDER BY reviews.id DESC
        """,
        (st.session_state["user_id"],)
    )

    my_reviews = cursor.fetchall()
    connection.close()

    if my_reviews:

        for review in my_reviews:

            reviewer_name = review[0]
            rating = review[1]
            review_text = review[2]

            st.write(f"👤 **{reviewer_name}**")
            st.write(f"⭐ **Rating:** {rating}/5")

            if review_text:
                st.write(
                    f"💬 **Review:** {review_text}"
                )

            st.divider()

    else:
        st.info("You don't have any reviews yet.")
