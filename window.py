import Quartz


class WindowManager(object):

    @classmethod
    def get_window_id(cls, app_name):
        window_info_list = cls._get_window_info_list()
        window_info_list = cls._filter_by_name(window_info_list, app_name)
        max_window = cls._max_area_window(window_info_list)
        return cls._window_id(max_window)

    @classmethod
    def _get_window_info_list(cls):
        window_info_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionAll, Quartz.kCGNullWindowID)
        return sorted(window_info_list,
                      key=lambda k: k.valueForKey_('kCGWindowOwnerPID'))

    @classmethod
    def _filter_by_name(cls, window_info_list, app_name):
        return [v for v in window_info_list
                if v['kCGWindowOwnerName'] == app_name]

    @classmethod
    def _max_area_window(cls, window_info_list):
        max_area = 0
        max_area_v = None
        for v in window_info_list:
            area = v['kCGWindowBounds']['Height'] * v['kCGWindowBounds'][
                'Width']
            if area > max_area:
                max_area = area
                max_area_v = v
        return max_area_v

    @classmethod
    def _window_id(cls, window_info):
        return window_info['kCGWindowNumber']

    @classmethod
    def _window_title(cls, window_info):
        return window_info['kCGWindowName']