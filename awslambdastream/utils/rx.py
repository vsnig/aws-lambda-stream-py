import rx

def from_subject(subj):
      def subscribe(observer, scheduler):
        return subj.subscribe(observer, scheduler)
      return rx.create(subscribe)