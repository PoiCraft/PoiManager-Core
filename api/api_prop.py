from flask import Flask

from api.api import BasicApi
from auth.Token import TokenManager
from core.bds import BdsCore
from database.BdsLogger import write_log
from loader.PropertiesLoader import PropertiesLoader


class Api_Prop(BasicApi):
    """The class of the API for the properties of bedrock server."""
    def __init__(self, app: Flask, token_manager: TokenManager, prop_loader: PropertiesLoader, bds: BdsCore):
        self.app = app
        self.tokenManager = token_manager
        self.propLoader = prop_loader
        self.bds = bds
        self.prop_all()
        self.prop_one()
        self.prop_one_set()
        self.prop_save()

    def prop_all(self):
        @self.app.route('/api/prop/all')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_prop_all():
            return self.get_body(
                body_code=200,
                body_type='prop_all',
                body_content=self.propLoader.prop,
                body_msg='OK',
                body_extra={
                    'edited': self.propLoader.if_edited(),
                    'saved': self.propLoader.if_saved()
                }
            )

    def prop_one(self):
        @self.app.route('/api/prop/one/<key>')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_prop_one(key):
            value = self.propLoader.get_prop(key)
            if value is None:
                return self.get_body(
                    body_code=404,
                    body_type=f'prop_{key}',
                    body_content=None,
                    body_msg='No such prop',
                    body_extra={
                        'edited': self.propLoader.if_edited(),
                        'saved': self.propLoader.if_saved()
                    }
                )
            else:
                return self.get_body(
                    body_code=200,
                    body_type=f'prop_{key}',
                    body_content=value,
                    body_msg='OK',
                    body_extra={
                        'edited': self.propLoader.if_edited(),
                        'saved': self.propLoader.if_saved()
                    }
                )

    def prop_one_set(self):
        @self.app.route('/api/prop/set/<key>/<value>')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_prop_set_one(key, value):
            _e = self.propLoader.edit_prop(key, value)
            return self.get_body(
                body_code=200,
                body_type=f'prop_edit_{key}',
                body_content=self.propLoader.prop,
                body_msg='OK',
                body_extra={
                    'edited': self.propLoader.if_edited(),
                    'saved': self.propLoader.if_saved()
                }
            )

    def prop_save(self):
        @self.app.route('/api/prop/save')
        @self.tokenManager.require_token
        @write_log(self.bds)
        def api_prop_save():
            self.propLoader.save()
            return self.get_body(
                body_code=200,
                body_type='prop_save',
                body_content=self.propLoader.prop,
                body_msg='OK',
                body_extra={
                    'edited': self.propLoader.if_edited(),
                    'saved': self.propLoader.if_saved()
                }
            )
