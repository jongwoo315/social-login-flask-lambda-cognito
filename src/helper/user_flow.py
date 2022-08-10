from abc import ABC, abstractmethod
from datetime import datetime
from src.helper.cognito import Cognito
from src.models.model import User, db_session


class NewUser:
    def __init__(self):
        self.new_user_data = {}
        self.cognito = Cognito()

    def add_data(self, flow, value):
        self.new_user_data[flow] = value
        
    def sign_up_user(self):
        sub = self.cognito.invoke_sign_up(
            self.new_user_data.get('platform'),
            self.new_user_data.get('user_id'),
            self.new_user_data.get('email'),
            self.new_user_data.get('screen_name'),
            self.new_user_data.get('profile_image_url')
        )

        self.cognito.invoke_admin_confirm_sign_up(
            self.new_user_data.get('platform'),
            self.new_user_data.get('user_id')
        )

        groups = self.cognito.invoke_list_groups()
        if not self.new_user_data.get('platform') in groups:
            self.cognito.invoke_create_group(self.new_user_data.get('platform'))

        self.cognito.invoke_admin_add_user_to_group(
            self.new_user_data.get('platform'),
            self.new_user_data.get('user_id'),
            self.new_user_data.get('platform')
        )

        user = User(
            sub=sub,
            cognito_username=f'{self.new_user_data.get("platform")}_{self.new_user_data.get("user_id")}',
            platform=self.new_user_data.get('platform'),
            user_id=self.new_user_data.get('user_id'),
            email=self.new_user_data.get('email'),
            screen_name=self.new_user_data.get('screen_name'),
            profile_image_url=self.new_user_data.get('profile_image_url')
        )
        db_session.add(user)
        db_session.commit()

        authentication_result = self.cognito.invoke_admin_initiate_auth(
            self.new_user_data.get('platform'),
            self.new_user_data.get('user_id')
        )
        return authentication_result, sub


class ExistingUser:
    def __init__(self) -> None:
        self.existing_user_data = {}
        self.cognito = Cognito()

    def add_data(self, flow, value):
        self.existing_user_data[flow] = value

    def update_user(self):
        self.cognito.invoke_admin_update_user_attributes(
            self.existing_user_data.get('platform'),
            self.existing_user_data.get('user_id'),
            self.existing_user_data.get('email'),
            self.existing_user_data.get('screen_name'),
            self.existing_user_data.get('profile_image_url')
        )

        user = db_session.query(User).filter_by(sub=self.existing_user_data.get('sub')).first()

        user.email = self.existing_user_data.get('email'),
        user.screen_name = self.existing_user_data.get('screen_name'),
        user.profile_image_url = self.existing_user_data.get('profile_image_url')
        user.update_date = datetime.now()

        db_session.merge(user)
        db_session.commit()

        authentication_result = self.cognito.invoke_admin_initiate_auth(
            self.existing_user_data.get('platform'),
            self.existing_user_data.get('user_id')
        )
        return authentication_result

    def unregister_user(self):
        self.cognito.invoke_admin_delete_user(
            self.existing_user_data.get('platform'),
            self.existing_user_data.get('user_id')
        )

        db_session.query(User).filter_by(sub=self.existing_user_data.get('sub')).delete()
        db_session.commit()


class Builder(ABC):
    @abstractmethod
    def fetch_sub(self) -> None:
        pass

    @abstractmethod
    def fetch_user_id(self) -> None:
        pass

    @abstractmethod
    def fetch_screen_name(self) -> None:
        pass

    @abstractmethod
    def fetch_picture(self) -> None:
        pass

    @abstractmethod
    def fetch_email(self) -> None:
        pass

    @abstractmethod
    def fetch_platform(self) -> None:
        pass


class NewUserBuilder(Builder):
    def __init__(self, user_info):
        self._new_user = NewUser()
        self.user_info = user_info

    @property
    def new_user(self):
        user = self._new_user
        return user

    def fetch_sub(self) -> None:
        """신규 사용자이므로 회원가입 단계에서 sub값을 받는다"""
        pass

    def fetch_user_id(self):
        self._new_user.add_data('user_id', self.user_info.get('user_id'))

    def fetch_screen_name(self):
        self._new_user.add_data('screen_name', self.user_info.get('screen_name'))

    def fetch_picture(self):
        self._new_user.add_data('profile_image_url', self.user_info.get('profile_image_url'))

    def fetch_email(self):
        self._new_user.add_data('email', self.user_info.get('email'))

    def fetch_platform(self):
        self._new_user.add_data('platform', self.user_info.get('platform'))


class ExistingUserBuilder(Builder):
    def __init__(self, user_info) -> None:
        self._existing_user = ExistingUser()
        self.user_info = user_info

    @property
    def existing_user(self):
        user = self._existing_user
        return user

    def fetch_sub(self):
        """기존 사용자이므로 cognito 사용자 체크함수에서 sub값을 받아온다"""
        self._existing_user.add_data('sub', self.user_info.get('sub'))

    def fetch_user_id(self):
        self._existing_user.add_data('user_id', self.user_info.get('user_id'))

    def fetch_screen_name(self):
        self._existing_user.add_data('screen_name', self.user_info.get('screen_name'))

    def fetch_picture(self):
        self._existing_user.add_data('profile_image_url', self.user_info.get('profile_image_url'))

    def fetch_email(self):
        self._existing_user.add_data('email', self.user_info.get('email'))

    def fetch_platform(self):
        self._existing_user.add_data('platform', self.user_info.get('platform'))


class Director:
    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder: Builder):
        self._builder = builder

    def load_user_data(self):
        self.builder.fetch_sub()
        self.builder.fetch_user_id()
        self.builder.fetch_screen_name()
        self.builder.fetch_picture()
        self.builder.fetch_email()
        self.builder.fetch_platform()
