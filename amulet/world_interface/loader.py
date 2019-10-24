from __future__ import annotations

import glob
import importlib.util
import json
import os
from typing import Tuple, AbstractSet, Any, Dict

from amulet.api.errors import LoaderNoneMatched


class Loader:
	def __init__(self, object_type: str, directory: str, supported_meta_version, supported_version):
		self._object_type = object_type
		self._directory = directory
		self._supported_meta_version = supported_meta_version
		self._supported_version = supported_version
		self._loaded: Dict[str, Any] = {}
		self._is_loaded = False

	def _find(self):
		"""Load all objects from the object directory"""

		directories = glob.iglob(os.path.join(self._directory, "*", ""))
		for d in directories:
			meta_path = os.path.join(d, f"{self._object_type}.meta")
			if not os.path.exists(meta_path):
				continue

			with open(meta_path) as fp:
				meta = json.load(fp)

			if meta["meta_version"] != self._supported_meta_version:
				print(
					f'[Error] Couldn\'t enable {self._object_type} located in "{d}" due to unsupported meta version'
				)
				continue

			if meta[self._object_type][f"{self._object_type}_version"] != self._supported_version:
				print(
					f"[Error] Couldn't enable {self._object_type} \"{meta[self._object_type]['id']}\" due to unsupported {self._object_type} version"
				)
				continue

			spec = importlib.util.spec_from_file_location(
				meta[self._object_type]["entry_point"],
				os.path.join(d, meta[self._object_type]["entry_point"] + ".py"),
			)
			modu = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(modu)

			if not hasattr(modu, f"{self._object_type.upper()}_CLASS"):
				print(
					f"[Error] {self._object_type} \"{meta[self._object_type]['id']}\" is missing the {self._object_type.upper()}_CLASS attribute"
				)
				continue

			self._loaded[meta[f"{self._object_type}"]["id"]] = modu.getattr(f"{self._object_type.upper()}_CLASS")()

			if __debug__:
				print(
					f"[Debug] Enabled {self._object_type} \"{meta[self._object_type]['id']}\", version {meta[self._object_type]['wrapper_version']}"
				)

		self._is_loaded = True

	def reload(self):
		"""Reloads all objects"""
		self._loaded.clear()
		self._find()

	def get_all_loaded(self) -> AbstractSet[str]:
		"""
		:return: The identifiers of all loaded objects
		"""
		if not self._is_loaded:
			self._find()
		return self._loaded.keys()

	def get(self, identifier: Tuple) -> Any:
		"""
		Given an ``identifier`` will find a valid class and return it

		:param identifier: The identifier for the desired loaded object
		:return: The class for the object
		"""
		object_id = self.identify(identifier)
		return self._loaded[object_id]

	def identify(self, identifier: Tuple) -> str:

		if not self._is_loaded:
			self._find()

		for object_name, object_instance in self._loaded.items():
			if object_instance.is_valid(identifier):
				return object_name

		raise LoaderNoneMatched(f"Could not find a matching {self._object_type}")

	def get_by_id(self, object_id: str):
		return self._loaded[object_id]
